"""
=====================================================================
📱 DASHBOARD PRINCIPAL (STREAMLIT)
=====================================================================

🎯 RÔLE DE CE FICHIER :
Ce fichier est le point d'entrée de l'application. Il crée l'interface
principale avec la barre latérale (sidebar) et charge les différentes pages.

🏗️ STRUCTURE :
- Configuration initiale de Streamlit
- Initialisation des variables de session (session_state)
- Barre latérale avec navigation (utilisation d'un callback)
- Affichage de la page sélectionnée (Accueil, Agent, Historique, Postuler, Analytics)

📚 CONCEPTS IMPORTANTS :
- st.session_state : dictionnaire persistant qui garde les données entre les rechargements
- callback : fonction appelée quand l'utilisateur interagit avec un widget
- source unique de vérité : st.session_state["page"] contrôle l'affichage

=====================================================================
"""

import streamlit as st
import sys
from pathlib import Path

# ==============================================================
# 🔧 CONFIGURATION DU CHEMIN PYTHON
# ==============================================================
# 📚 EXPLICATION :
# Python doit savoir où trouver les modules à importer.
# On ajoute le dossier racine du projet (agent_job_search) au chemin de recherche.
# Cela permet d'importer des modules comme "dashboard.pages.Agent_1"

# Récupère le dossier parent du fichier actuel (app.py)
# __file__ = chemin complet de ce fichier
# .parent = remonte d'un niveau (de app.py vers dashboard)
# .parent = remonte encore (de dashboard vers agent_job_search)
root_dir = Path(__file__).parent.parent

# Si le dossier racine n'est pas déjà dans le chemin Python, on l'ajoute
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# ==============================================================
# ⚙️ CONFIGURATION DE LA PAGE STREAMLIT
# ==============================================================
# 📚 EXPLICATION :
# Ces réglages s'appliquent à TOUTE l'application.
# Ils doivent être placés AVANT tout autre élément Streamlit.

st.set_page_config(
    page_title="AI Job Agent",           # Titre dans l'onglet du navigateur
    page_icon="🤖",                      # Icône dans l'onglet
    layout="wide",                       # "wide" = utilise toute la largeur de l'écran
    initial_sidebar_state="expanded"     # "expanded" = barre latérale ouverte par défaut
)

# ==============================================================
# 🧠 SESSION STATE - MÉMOIRE PERSISTANTE
# ==============================================================
# 📚 EXPLICATION :
# st.session_state est comme un dictionnaire qui garde les données
# même quand Streamlit recharge la page (ce qui arrive à chaque interaction).

# --- Variable qui contrôle quelle page est affichée ---
# C'est la SOURCE UNIQUE DE VÉRITÉ pour la navigation
if "page" not in st.session_state:
    st.session_state["page"] = "🏠 Accueil"  # Page par défaut

# --- Offre sélectionnée pour postuler ---
# Utilisée quand l'utilisateur clique sur "Postuler" dans la page Agent
if "selected_offer" not in st.session_state:
    st.session_state.selected_offer = None

# --- Résultats de l'agent (offres trouvées) ---
if "agent_results" not in st.session_state:
    st.session_state.agent_results = None

# --- CV utilisé lors de la dernière recherche ---
if "cv_used" not in st.session_state:
    st.session_state.cv_used = None

# --- État de connexion à l'API ---
if "api_connected" not in st.session_state:
    st.session_state.api_connected = False

# ==============================================================
# 🧭 BARRE LATÉRALE (SIDEBAR) - NAVIGATION
# ==============================================================
# 📚 EXPLICATION :
# La barre latérale contient le menu de navigation.
# On utilise un callback pour mettre à jour session_state UNIQUEMENT
# quand l'utilisateur clique sur un bouton. Cela évite d'écraser les
# changements de page faits par le bouton "Postuler".

st.sidebar.title("📋 Navigation")
st.sidebar.markdown("---")

# --- Liste des pages disponibles ---
# Ces noms doivent correspondre exactement à ceux utilisés dans les conditions
pages = [
    "🏠 Accueil",           # Page d'accueil (intégrée dans app.py)
    "🎯 Lancer l'agent",    # Page Agent (Agent_1.py)
    "📜 Historique",        # Page Historique (Historique_2.py)
    "✍️ Postuler",          # Page Postuler (Apply_3.py)
    "📊 Analytics"          # Page Analytics (Analytics_4.py)
]

# --- Fonction callback pour la navigation ---
# 📚 EXPLICATION :
# Cette fonction est appelée automatiquement quand l'utilisateur change
# la sélection dans le radio button. Elle met à jour session_state.
def on_page_change():
    """Met à jour la page dans session_state quand l'utilisateur change de page."""
    st.session_state["page"] = st.session_state["nav_radio"]

# --- Radio button avec callback ---
# 📚 EXPLICATION :
# key="nav_radio" : permet d'accéder à la valeur sélectionnée dans le callback
# on_change=on_page_change : fonction appelée quand la valeur change
st.sidebar.radio(
    label="Choisis une page :",
    options=pages,
    index=pages.index(st.session_state["page"]),  # Pré-sélectionne la page actuelle
    key="nav_radio",                               # Clé pour accéder à la valeur
    on_change=on_page_change                       # Callback sur changement
)

st.sidebar.markdown("---")

# ==============================================================
# 🔌 VÉRIFICATION DE LA CONNEXION À L'API
# ==============================================================
# 📚 EXPLICATION :
# On teste si le backend FastAPI (sur le port 8000) est accessible.
# Un indicateur s'affiche dans la sidebar.

try:
    import requests
    
    # Envoie une requête GET à l'endpoint /health
    response = requests.get("http://localhost:8000/health", timeout=2)
    
    if response.status_code == 200:
        st.session_state.api_connected = True
    else:
        st.session_state.api_connected = False
        
except Exception:
    # Si la connexion échoue (serveur non démarré, erreur réseau, etc.)
    st.session_state.api_connected = False

# --- Affichage de l'indicateur de connexion ---
if st.session_state.api_connected:
    st.sidebar.success("✅ API connectée")
else:
    st.sidebar.warning("⚠️ API non connectée")
    st.sidebar.markdown(
        "Assure-toi que le backend est lancé :\n\n"
        "`uvicorn app.main:app --reload`"
    )

st.sidebar.markdown("---")
st.sidebar.info("💡 Astuce : Uploade ton CV pour commencer !")

# ==============================================================
# 📄 AFFICHAGE DE LA PAGE SÉLECTIONNÉE
# ==============================================================
# 📚 EXPLICATION :
# On récupère la page actuelle depuis session_state et on affiche
# le contenu correspondant. C'est le CŒUR de l'application.

current_page = st.session_state["page"]

# ==============================================================
# 🏠 PAGE 1 : ACCUEIL
# ==============================================================
if current_page == "🏠 Accueil":
    """
    Page d'accueil - présentation de l'application
    Cette page est intégrée directement dans app.py
    """
    
    st.title("🤖 AI Job Agent")
    st.markdown("""
    ### 👋 Bienvenue dans ton agent intelligent de recherche d'emploi !
    
    Cet assistant va t'aider à :
    
    ✅ **Analyser ton CV** et le comparer avec des offres d'emploi  
    ✅ **Trouver les meilleures opportunités** selon ton profil  
    ✅ **Générer des candidatures personnalisées** (CV + lettre de motivation)  
    ✅ **Suivre tes candidatures** et analyser tes performances  
    
    ### 🚀 Pour commencer :
    1. Va dans la page **"Lancer l'agent"** (dans le menu de gauche)
    2. Uploade ton CV (format PDF)
    3. Lance l'analyse automatique
    4. Consulte les offres recommandées
    
    ### 📊 Fonctionnalités :
    - **Score de compatibilité** : évalue la correspondance entre ton CV et l'offre
    - **Filtres intelligents** : trie par score, localisation, etc.
    - **Génération automatique** : crée des lettres de motivation personnalisées
    - **Historique complet** : garde une trace de toutes tes candidatures
    """)
    
    st.info("🔍 Commence par uploader ton CV dans la page 'Lancer l'agent' !")

# ==============================================================
# 🎯 PAGE 2 : LANCER L'AGENT
# ==============================================================
elif current_page == "🎯 Lancer l'agent":
    """
    Page principale : recherche d'offres d'emploi
    Cette page permet de lancer l'agent IA pour analyser les offres
    """
    try:
        from dashboard.pages import Agent_1
        
        if hasattr(Agent_1, 'show'):
            Agent_1.show()
        else:
            st.error("❌ La fonction show() n'existe pas dans Agent_1.py")
    except ImportError as e:
        st.error(f"❌ Impossible d'importer Agent_1")
        st.write(f"Erreur détaillée : {e}")
    except Exception as e:
        st.error(f"❌ Erreur inattendue dans la page Agent")
        st.write(f"Erreur : {e}")

# ==============================================================
# 📜 PAGE 3 : HISTORIQUE
# ==============================================================
elif current_page == "📜 Historique":
    """
    Page Historique : affiche les candidatures précédentes
    """
    try:
        from dashboard.pages import Historique_2
        
        if hasattr(Historique_2, 'show'):
            Historique_2.show()
        else:
            st.error("❌ La fonction show() n'existe pas dans Historique_2.py")
    except ImportError as e:
        st.error(f"❌ Impossible d'importer Historique_2")
        st.write(f"Erreur : {e}")
    except Exception as e:
        st.error(f"❌ Erreur : {e}")

# ==============================================================
# ✍️ PAGE 4 : POSTULER
# ==============================================================
elif current_page == "✍️ Postuler":
    """
    Page Postuler : génère une lettre de motivation personnalisée
    """
    try:
        from dashboard.pages import Apply_3
        
        if hasattr(Apply_3, 'show'):
            Apply_3.show()
        else:
            st.error("❌ La fonction show() n'existe pas dans Apply_3.py")
    except ImportError as e:
        st.error(f"❌ Impossible d'importer Apply_3")
        st.write(f"Erreur : {e}")
    except Exception as e:
        st.error(f"❌ Erreur : {e}")

# ==============================================================
# 📊 PAGE 5 : ANALYTICS
# ==============================================================
elif current_page == "📊 Analytics":
    """
    Page Analytics : statistiques et graphiques sur les candidatures
    """
    try:
        from dashboard.pages import Analytics_4
        
        if hasattr(Analytics_4, 'show'):
            Analytics_4.show()
        else:
            st.error("❌ La fonction show() n'existe pas dans Analytics_4.py")
    except ImportError as e:
        st.error(f"❌ Impossible d'importer Analytics_4")
        st.write(f"Erreur : {e}")
    except Exception as e:
        st.error(f"❌ Erreur : {e}")

# ==============================================================
# 🚫 PAGE NON RECONNUE (cas d'erreur)
# ==============================================================
else:
    """
    Ce bloc ne devrait jamais s'exécuter si tout fonctionne correctement.
    Il sert de sécurité.
    """
    st.warning(f"⚠️ Page inconnue : {current_page}")
    st.info("Utilise la barre latérale pour naviguer vers une page valide.")
    
    if st.button("🏠 Retour à l'accueil"):
        st.session_state["page"] = "🏠 Accueil"
        st.rerun()