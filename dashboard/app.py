import streamlit as st
import sys
import os
from pathlib import Path

# Configuration de la page
st.set_page_config(
    page_title="AI Job Agent",
    page_icon="🤖",
    layout="wide"
)

# Ajouter le dossier racine au PYTHONPATH pour permettre les imports
root_dir = Path(__file__).parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Titre principal
st.title("🤖 AI Job Agent")

# Sidebar pour la navigation
st.sidebar.title("📋 Navigation")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Choisis une page :",
    [
        "🏠 Accueil",
        "🎯 Lancer l'agent",
        "📜 Historique",
        "✍️ Postuler",
        "📊 Analytics"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 Astuce : Uploade ton CV pour commencer !")

# Afficher la page sélectionnée
if page == "🏠 Accueil":
    st.markdown("""
    ### 👋 Bienvenue dans ton agent intelligent de recherche d'emploi !
    
    Cet assistant va t'aider à :
    
    ✅ **Analyser ton CV** et le comparer avec des offres d'emploi  
    ✅ **Trouver les meilleures opportunités** selon ton profil  
    ✅ **Générer des candidatures personnalisées** (CV + lettre de motivation)  
    ✅ **Suivre tes candidatures** et analyser tes performances  
    
    ### 🚀 Pour commencer :
    1. Va dans la page **"Lancer l'agent"**
    2. Uploade ton CV (format PDF)
    3. Lance l'analyse automatique
    4. Consulte les offres recommandées
    
    ### 📊 Fonctionnalités :
    - **Score de compatibilité** : évalue la correspondance entre ton CV et l'offre
    - **Filtres intelligents** : trie par score, localisation, etc.
    - **Génération automatique** : crée des lettres de motivation personnalisées
    - **Historique complet** : garde une trace de toutes tes candidatures
    """)
    
elif page == "🎯 Lancer l'agent":
    # Importer et exécuter la page Agent
    try:
        # Solution 1: exécuter le fichier directement
        with open("dashboard/pages/1_Agent.py", "r", encoding="utf-8") as f:
            exec(f.read())
    except FileNotFoundError:
        st.error("❌ Fichier dashboard/pages/1_Agent.py introuvable")
        st.info("Vérifie que le fichier existe bien à cet emplacement")
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement de la page: {e}")
        
elif page == "📜 Historique":
    try:
        with open("dashboard/pages/2_Historique.py", "r", encoding="utf-8") as f:
            exec(f.read())
    except FileNotFoundError:
        st.info("📭 Page Historique en cours de développement")
        st.markdown("""
        ### Historique des candidatures
        
        Cette page affichera bientôt :
        - Toutes tes candidatures envoyées
        - Le statut de chaque candidature
        - Les lettres de motivation générées
        - Les dates d'envoi
        """)
    except Exception as e:
        st.error(f"❌ Erreur: {e}")
        
elif page == "✍️ Postuler":
    try:
        with open("dashboard/pages/3_Apply.py", "r", encoding="utf-8") as f:
            exec(f.read())
    except FileNotFoundError:
        st.info("📝 Page Apply en cours de développement")
        st.markdown("""
        ### Postuler à une offre
        
        Cette page te permettra de :
        - Sélectionner une offre d'emploi
        - Générer une lettre de motivation personnalisée
        - Adapter ton CV à l'offre
        - Envoyer ta candidature
        """)
    except Exception as e:
        st.error(f"❌ Erreur: {e}")
        
elif page == "📊 Analytics":
    try:
        with open("dashboard/pages/4_Analytics.py", "r", encoding="utf-8") as f:
            exec(f.read())
    except FileNotFoundError:
        st.info("📈 Page Analytics en cours de développement")
        st.markdown("""
        ### Statistiques et Analytics
        
        Cette page affichera :
        - Taux de réponse par secteur
        - Évolution des scores de match
        - Meilleures périodes de candidature
        - Recommandations personnalisées
        """)
    except Exception as e:
        st.error(f"❌ Erreur: {e}")