"""
=====================================================================
🎯 PAGE AGENT - LANCEMENT DE L'AGENT AUTONOME
=====================================================================

🎯 RÔLE DE CETTE PAGE :
Cette page permet à l'utilisateur de :
- Choisir un CV (par défaut, existant, ou en uploader un nouveau)
- Configurer les paramètres de recherche (nombre d'offres, localisation, seuil)
- Lancer l'agent IA pour analyser les offres
- Afficher les résultats avec les scores de matching
- Rediriger vers la page de candidature

📦 COMPOSANTS UTILISÉS :
- job_card.py : Affiche chaque offre d'emploi sous forme de carte
- user_config_service.py : Récupère les coordonnées utilisateur (pour les lettres)

=====================================================================
"""

import streamlit as st
import requests
import sys
import os
from pathlib import Path

# ==============================================================
# 🔧 CONFIGURATION DES IMPORTS (pour que les modules soient trouvés)
# ==============================================================

# Ajouter la racine du projet au PYTHONPATH
# Cela permet d'importer correctement les modules même si on lance depuis un sous-dossier
root_dir = Path(__file__).parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Import du composant job_card pour l'affichage des offres
from dashboard.components.job_card import display_job

# Configuration de l'API backend
API_BASE_URL = "http://localhost:8000"


# ==============================================================
# 🔧 FONCTIONS UTILITAIRES
# ==============================================================

@st.cache_data(ttl=60)
def get_cv_list():
    """
    Récupère la liste des CV depuis le backend.
    
    📚 EXPLICATION :
    @st.cache_data(ttl=60) : met en cache le résultat pendant 60 secondes.
    Cela évite de rappeler l'API à chaque rechargement de la page.
    
    Returns:
        tuple: (liste des CV, dernier CV utilisé)
    """
    try:
        response = requests.get(f"{API_BASE_URL}/agent/cv/list", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("cvs", []), data.get("last_cv")
        return [], None
    except Exception as e:
        st.error(f"Erreur de connexion au backend : {e}")
        st.info("💡 Vérifie que le backend FastAPI est bien lancé sur http://localhost:8000")
        return [], None


def run_agent(cv_name, file, max_jobs, location, threshold):
    """
    Envoie la requête au backend pour lancer l'agent.
    
    📚 EXPLICATION :
    Cette fonction construit la requête POST vers l'API FastAPI.
    Selon le type de CV choisi, elle envoie soit un nom de CV existant,
    soit un fichier PDF à uploader.
    
    Args:
        cv_name (str, optional): Nom du CV existant
        file (UploadedFile, optional): Fichier PDF uploadé
        max_jobs (int): Nombre d'offres à chercher
        location (str): Localisation (ville)
        threshold (int): Seuil de matching (0-100)
    
    Returns:
        dict: Résultats de l'agent (offres analysées) ou None en cas d'erreur
    """
    try:
        # Construction des données à envoyer
        data = {
            "max_jobs": max_jobs,
            "location": location,
            "match_threshold": threshold
        }
        files = None
        
        # Gestion du CV selon l'option choisie
        if file:
            # Cas 1 : Upload d'un nouveau CV
            files = {"file": (file.name, file.getvalue(), "application/pdf")}
        elif cv_name:
            # Cas 2 : Utilisation d'un CV existant
            data["cv_name"] = cv_name
        # Cas 3 : CV par défaut (rien à ajouter, le backend utilisera le CV par défaut)

        # Envoi de la requête POST
        response = requests.post(
            f"{API_BASE_URL}/agent/run",
            data=data,
            files=files,
            timeout=120  # Timeout long car l'agent peut être lent (30-60 secondes)
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erreur {response.status_code}: {response.text}")
            return None
    except requests.exceptions.Timeout:
        st.error("⏰ La requête a expiré. L'agent a pris trop de temps à répondre.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("🔌 Impossible de se connecter au backend. Vérifie que le serveur FastAPI est lancé.")
        return None
    except Exception as e:
        st.error(f"❌ Erreur de connexion : {e}")
        return None


# ==============================================================
# 📄 FONCTION PRINCIPALE D'AFFICHAGE
# ==============================================================

def show():
    """
    Fonction principale qui affiche la page Agent.
    C'est cette fonction qui est appelée par app.py.
    """
    
    # ==========================================================
    # TITRE ET RÉCUPÉRATION DES CV
    # ==========================================================
    st.title("🎯 Lancer l'agent")
    st.markdown("Lance l'agent IA pour rechercher des offres d'emploi correspondant à ton profil.")

    # Récupération de la liste des CV
    cv_data, last_cv = get_cv_list()

    # Transformation des données en liste de noms de fichiers
    # L'API peut retourner deux formats différents :
    # - Format 1 : liste de dictionnaires (avec métadonnées)
    # - Format 2 : liste simple de noms
    if cv_data and isinstance(cv_data[0], dict):
        # Format avec dictionnaires
        cv_names = [cv.get("filename") for cv in cv_data if cv.get("filename")]
    else:
        # Format avec liste simple
        cv_names = cv_data

    # ==========================================================
    # FORMULAIRE DE RECHERCHE
    # ==========================================================
    # 📚 EXPLICATION :
    # On utilise st.form() pour regrouper tous les widgets.
    # La page ne se recharge qu'au clic sur le bouton de soumission.
    with st.form(key="search_form"):
        st.markdown("## 📄 CV")

        # Bouton radio pour choisir le type de CV
        cv_option = st.radio(
            "Choix du CV",
            ["CV par défaut", "CV existant", "Upload nouveau CV"],
            horizontal=True,
            help="Sélectionne le CV à utiliser pour l'analyse"
        )

        # Initialisation des variables (seront remplacées si besoin)
        selected_cv = None
        uploaded_file = None

        # Affichage conditionnel selon l'option choisie
        if cv_option == "CV existant":
            if cv_names:
                # Calcul de l'index par défaut (dernier CV utilisé si possible)
                default_idx = cv_names.index(last_cv) if last_cv in cv_names else 0
                # Liste déroulante pour choisir un CV existant
                selected_cv = st.selectbox(
                    "Choisir un CV", 
                    cv_names, 
                    index=default_idx,
                    help="Sélectionne un CV déjà uploadé"
                )
            else:
                st.warning("⚠️ Aucun CV disponible. Uploade un CV d'abord.")
                
        elif cv_option == "Upload nouveau CV":
            # Champ pour uploader un nouveau CV (PDF uniquement)
            uploaded_file = st.file_uploader(
                "Fichier PDF", 
                type=["pdf"],
                help="Upload un CV au format PDF"
            )

        # Séparateur visuel
        st.markdown("---")
        
        # Paramètres de recherche
        st.markdown("## ⚙️ Paramètres de recherche")

        # Création de 3 colonnes pour aligner les widgets
        col1, col2, col3 = st.columns(3)
        
        with col1:
            max_jobs = st.number_input(
                "Nombre d'offres",
                min_value=1,
                max_value=20,
                value=5,
                help="Nombre maximum d'offres à analyser"
            )
        
        with col2:
            location = st.text_input(
                "Localisation",
                value="Rennes",
                help="Ville où chercher les offres (ex: Paris, Lyon, Remote)"
            )
        
        with col3:
            threshold = st.slider(
                "Seuil de matching (%)",
                0, 100, 50,
                help="Score minimum pour qu'une offre soit recommandée (0-100)"
            )

        # Bouton de soumission
        submitted = st.form_submit_button(
            "🚀 LANCER L'AGENT",
            type="primary",
            use_container_width=True
        )

    # ==========================================================
    # TRAITEMENT DE LA RECHERCHE (après clic)
    # ==========================================================
    if submitted:
        # Validation 1 : CV existant mais rien sélectionné
        if cv_option == "CV existant" and not selected_cv and cv_names:
            st.error("❌ Aucun CV sélectionné")
        
        # Validation 2 : Upload mais pas de fichier
        elif cv_option == "Upload nouveau CV" and not uploaded_file:
            st.error("❌ Aucun fichier uploadé")
        
        # Tout est valide, on lance l'agent
        else:
            with st.spinner("🤖 Analyse en cours... (peut prendre 30-60 secondes)"):
                result = run_agent(
                    cv_name=selected_cv if cv_option == "CV existant" else None,
                    file=uploaded_file if cv_option == "Upload nouveau CV" else None,
                    max_jobs=max_jobs,
                    location=location,
                    threshold=threshold
                )

                if result:
                    # Stockage des résultats dans session_state
                    st.session_state["agent_results"] = result.get("jobs", [])
                    st.session_state["cv_used"] = result.get("cv_used", "inconnu")
                    st.session_state["search_params"] = {
                        "location": location,
                        "threshold": threshold,
                        "max_jobs": max_jobs
                    }
                    st.success(f"✅ {result.get('message', 'Analyse terminée avec succès !')}")

    # ==========================================================
    # AFFICHAGE DES RÉSULTATS
    # ==========================================================
    if st.session_state.get("agent_results"):
        jobs = st.session_state["agent_results"]
        cv_used = st.session_state.get("cv_used", "inconnu")
        search_params = st.session_state.get("search_params", {})

        st.markdown("---")
        st.markdown("## 📊 Résultats de l'analyse")
        
        # Afficher un récapitulatif des paramètres utilisés
        with st.expander("📋 Récapitulatif de la recherche"):
            st.markdown(f"**CV utilisé :** {cv_used}")
            st.markdown(f"**Localisation :** {search_params.get('location', 'Non spécifiée')}")
            st.markdown(f"**Seuil de matching :** {search_params.get('threshold', 50)}%")
            st.markdown(f"**Nombre d'offres demandé :** {search_params.get('max_jobs', 5)}")
            st.markdown(f"**Offres trouvées :** {len(jobs)}")

        if jobs:
            # Afficher le nombre d'offres trouvées
            st.markdown(f"### 📋 {len(jobs)} offre(s) trouvée(s)")
            
            # ✅ UTILISATION DU COMPOSANT JOB_CARD
            # 📚 EXPLICATION :
            # Le composant display_job s'occupe de tout l'affichage :
            # - Titre, entreprise, localisation
            # - Score avec badge coloré
            # - Barre de progression
            # - Compétences manquantes et points forts
            # - Bouton "Postuler"
            # - Gestion automatique des valeurs par défaut
            # - Nettoyage des données (adresse perso, messages de test)
            
            for idx, job in enumerate(jobs):
                # Ajouter l'index pour faciliter le débogage si besoin
                job["_index"] = idx
                
                # Afficher l'offre avec le composant job_card
                # Le composant gère automatiquement :
                # - L'affichage de la localisation (sans l'adresse perso)
                # - Le nettoyage des messages de test
                # - La gestion des valeurs manquantes
                display_job(job)
                
                # Séparateur visuel entre les offres (sauf pour la dernière)
                if idx < len(jobs) - 1:
                    st.markdown("---")
            
            # Message d'aide après l'affichage des offres
            st.info("💡 **Astuce :** Clique sur le bouton 'Postuler' pour générer une lettre de motivation personnalisée.")
            
        else:
            # Aucune offre trouvée après analyse
            st.warning("😕 Aucune offre d'emploi trouvée")
            st.markdown("""
            **Suggestions pour améliorer les résultats :**
            - Élargis la zone géographique (ex: essayer 'France' ou 'Remote')
            - Abaisse le seuil de matching
            - Augmente le nombre d'offres recherchées
            - Vérifie que ton CV est bien formaté
            """)

    else:
        # Message d'accueil quand aucun résultat n'est encore disponible
        if not submitted:
            st.info("👋 **Prêt à commencer ?**")
            st.markdown("""
            **Pour lancer une recherche :**
            1. Sélectionne un CV (par défaut, existant ou upload un nouveau)
            2. Configure tes paramètres de recherche (localisation, seuil, nombre d'offres)
            3. Clique sur "LANCER L'AGENT"
            
            L'agent IA va analyser ton CV et trouver les offres qui correspondent le mieux à ton profil.
            """)


# ==============================================================
# 🔧 EXÉCUTION DIRECTE (pour test)
# ==============================================================

if __name__ == "__main__":
    show()