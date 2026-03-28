"""
📦 JOB CARD COMPONENT
======================
Affiche une carte UI pour chaque offre d'emploi avec :
- Titre, entreprise, score
- Badge de score (HIGH/MEDIUM/LOW)
- Barre de progression
- Lettre de motivation (optionnelle)
- Bouton de candidature

🔒 SÉCURITÉ :
- Nettoie automatiquement les données personnelles (adresse utilisateur)
- Supprime les messages de test
- Évite l'affichage de données sensibles
"""

import streamlit as st
import hashlib


# ==========================================================
# 🔧 FONCTION DE NETTOYAGE DES DONNÉES
# ==========================================================

def clean_location(location: str) -> str:
    """
    Nettoie la localisation pour éviter d'afficher des données personnelles.
    
    Args:
        location (str): Localisation brute de l'offre
    
    Returns:
        str: Localisation nettoyée ou message par défaut
    """
    if not location or location.strip() == "":
        return "📍 Localisation non spécifiée"
    
    # Liste des motifs à supprimer (données personnelles, messages de test)
    forbidden_patterns = [
        "Square des Collines",
        "24 Square",
        "35000 Rennes",
        "p.gankama@gmail.com",
        "06 41 38 92 88",
        "Tests et diagnostic",
        "Tests et diagnostic de production",
        "niveau 1",
        "niveau 2",
        "niveau 3"
    ]
    
    # Nettoyer la localisation
    cleaned = location
    for pattern in forbidden_patterns:
        if pattern in cleaned:
            cleaned = cleaned.replace(pattern, "").strip()
    
    # Si après nettoyage il ne reste rien, afficher message par défaut
    if not cleaned or cleaned.strip() == "" or cleaned == location:
        return "📍 Localisation non spécifiée"
    
    return f"📍 {cleaned}"


def clean_description(description: str) -> str:
    """
    Nettoie la description pour supprimer les messages de test.
    
    Args:
        description (str): Description brute de l'offre
    
    Returns:
        str: Description nettoyée
    """
    if not description:
        return ""
    
    # Supprimer les messages de test
    forbidden_patterns = [
        "Tests et diagnostic",
        "Tests et diagnostic de production",
        "niveau 1",
        "niveau 2",
        "niveau 3"
    ]
    
    cleaned = description
    for pattern in forbidden_patterns:
        if pattern in cleaned:
            cleaned = cleaned.replace(pattern, "").strip()
    
    return cleaned


def clean_title(title: str) -> str:
    """
    Nettoie le titre pour supprimer les messages de test.
    
    Args:
        title (str): Titre brut de l'offre
    
    Returns:
        str: Titre nettoyé
    """
    if not title:
        return "Titre non disponible"
    
    forbidden_patterns = [
        "Tests et diagnostic",
        "Tests et diagnostic de production",
        "niveau 1"
    ]
    
    cleaned = title
    for pattern in forbidden_patterns:
        if pattern in cleaned:
            cleaned = cleaned.replace(pattern, "").strip()
    
    return cleaned if cleaned else "Titre non disponible"


# ==========================================================
# 🃏 FONCTION PRINCIPALE D'AFFICHAGE
# ==========================================================

def display_job(job: dict) -> None:
    """
    🎯 Affiche un job sous forme de carte UI interactive

    Args:
        job (dict): Dictionnaire contenant les informations de l'offre
            Clés attendues:
            - title (str): Titre du poste
            - company (str): Nom de l'entreprise
            - score (int/float): Score de compatibilité (0-100)
            - decision (str): "APPLY" ou "SKIP"
            - cover_letter (str, optionnel): Lettre de motivation générée
            - location (str, optionnel): Localisation
            - url (str, optionnel): Lien vers l'offre
            - description (str, optionnel): Description du poste
    """

    # ==========================================================
    # 📋 RÉCUPÉRATION DES INFORMATIONS AVEC NETTOYAGE
    # ==========================================================
    # Nettoyer le titre (supprime les messages de test)
    title = clean_title(job.get("title", "N/A"))
    company = job.get("company", "N/A")
    score = job.get("score", 0)
    decision = job.get("decision", "UNKNOWN")
    
    # ✅ NETTOYAGE DE LA LOCALISATION (supprime l'adresse personnelle)
    raw_location = job.get("location", "")
    location_display = clean_location(raw_location)
    
    url = job.get("url", "#")
    
    # ✅ NETTOYAGE DE LA DESCRIPTION (supprime les messages de test)
    raw_description = job.get("description", "")
    description = clean_description(raw_description)

    # ==========================================================
    # 🎨 BADGE DE SCORE
    # ==========================================================
    # Définit le badge et sa couleur en fonction du score
    if score >= 80:
        badge = "🔥 HIGH"      # Excellent match
        score_color = "green"
    elif score >= 60:
        badge = "⚡ MEDIUM"    # Bon match
        score_color = "orange"
    elif score >= 40:
        badge = "⚠️ FAIR"      # Match moyen
        score_color = "gold"
    else:
        badge = "❌ LOW"       # Faible correspondance
        score_color = "red"

    # Couleur pour la décision (APPLY = vert, SKIP = rouge)
    decision_color = "green" if decision == "APPLY" else "red"

    # ==========================================================
    # 🃏 AFFICHAGE DE LA CARTE
    # ==========================================================
    with st.container():

        # Ligne 1: Titre + Score
        col1, col2 = st.columns([3, 1])

        with col1:
            # Titre du poste avec emoji
            st.markdown(f"### 💼 {title}")
            # Entreprise et localisation (nettoyée)
            st.write(f"🏢 **{company}** • {location_display}")

        with col2:
            # Score affiché dans une métrique
            st.metric("🎯 Score", f"{score}%")
            # Badge de décision
            st.markdown(f"**:{decision_color}[{decision}]**")

        # Ligne 2: Badge de score
        st.markdown(f"**:{score_color}[{badge}]**")

        # Barre de progression visuelle du score
        st.progress(score / 100)

        # ==========================================================
        # 📄 DESCRIPTION (optionnelle, nettoyée)
        # ==========================================================
        if description and description.strip():
            with st.expander("📋 Description du poste"):
                # Troncature si trop long
                if len(description) > 500:
                    st.write(description[:500] + "...")
                else:
                    st.write(description)

        # ==========================================================
        # 📩 LETTRE DE MOTIVATION (optionnelle)
        # ==========================================================
        if "cover_letter" in job and job["cover_letter"]:
            with st.expander("📩 Lettre de motivation"):
                st.write(job["cover_letter"])
        elif decision == "APPLY":
            # Option pour générer une lettre si pas encore faite
            if st.button("✍️ Générer lettre de motivation", key=f"gen_letter_{hashlib.md5(title.encode()).hexdigest()[:8]}"):
                st.info("⏳ Fonctionnalité à implémenter")

        # ==========================================================
        # 🔗 LIEN VERS L'OFFRE (optionnel)
        # ==========================================================
        if url and url != "#":
            st.markdown(f"[🔗 Voir l'offre originale]({url})")

        # ==========================================================
        # 🚀 BOUTON POSTULER AVEC REDIRECTION
        # ==========================================================
        # Création d'un identifiant unique pour le bouton
        job_id = hashlib.md5(f"{title}_{company}".encode()).hexdigest()[:8]
        
        if st.button(
            f"📝 Postuler à {title}",
            key=f"apply_{job_id}",
            type="primary" if decision == "APPLY" else "secondary",
            use_container_width=True
        ):
            # Stocke l'offre sélectionnée dans la session
            st.session_state["selected_job"] = job
            st.session_state["selected_job_title"] = title
            st.session_state["selected_job_company"] = company
            
            # ✅ REDIRECTION VERS LA PAGE DE CANDIDATURE
            # Option 1: Utiliser st.switch_page (Streamlit >= 1.27.0)
            try:
                st.switch_page("dashboard/pages/Apply_3.py")
            except:
                # Fallback: changer la page via session_state
                st.session_state["page"] = "✍️ Postuler"
                st.rerun()


def display_jobs_list(jobs: list, show_apply_button: bool = True) -> None:
    """
    🎯 Affiche une liste d'offres d'emploi

    Args:
        jobs (list): Liste des dictionnaires d'offres
        show_apply_button (bool): Afficher ou non les boutons de candidature
    """
    if not jobs:
        st.info("📭 Aucune offre à afficher")
        return

    # Affichage du nombre d'offres
    st.caption(f"📊 {len(jobs)} offre(s) trouvée(s)")

    # Affichage de chaque offre
    for job in jobs:
        display_job(job)


# ==========================================================
# 🔧 FONCTION UTILITAIRE POUR LE DÉBOGAGE
# ==========================================================

def debug_job_structure(job: dict) -> None:
    """
    🔍 Affiche la structure d'un job pour le débogage
    Utile pour comprendre les données reçues de l'API
    """
    with st.expander("🔧 Debug: Structure de l'offre"):
        st.json({
            "keys": list(job.keys()),
            "sample": {k: str(v)[:100] for k, v in job.items()}
        })