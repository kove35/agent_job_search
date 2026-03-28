"""
=====================================================================
⚙️ CONFIGURATION CENTRALE - POINT D'ENTRÉE DE TOUTES LES CONFIGURATIONS
=====================================================================

🎯 RÔLE DE CE FICHIER :
Ce fichier est le "centre de contrôle" de l'application.
C'est ici que sont stockées TOUTES les configurations :
- Clés API (OpenAI, Adzuna)
- Paramètres de l'IA
- Chemins des fichiers
- Critères de recherche d'emploi
- Seuils de décision

📚 POUR UN DÉBUTANT :
Imagine ce fichier comme le "tableau de bord" de l'application.
Toutes les variables qui peuvent changer selon l'environnement
sont regroupées ici. Si tu veux modifier le comportement de
l'application (changer la ville de recherche, ajuster le score
minimum, etc.), c'est ici que ça se passe.

🔄 FLUX DE DONNÉES :
1. Le fichier .env est chargé (clés API sensibles)
2. La fonction get_env() vérifie que les clés sont présentes
3. La classe Settings regroupe toutes les configs
4. Une instance unique 'settings' est créée
5. Les autres fichiers importent 'settings' pour l'utiliser

=====================================================================
"""

# ==============================================================
# 🔹 IMPORTS
# ==============================================================

import os  # Pour interagir avec le système de fichiers
from dotenv import load_dotenv  # Pour charger le fichier .env


# ==============================================================
# 🔹 CHARGEMENT DU FICHIER .env
# ==============================================================

# 📚 EXPLICATION :
# Le fichier .env contient les informations SENSIBLES (clés API)
# Il n'est PAS commité sur GitHub pour des raisons de sécurité.
# load_dotenv() lit ce fichier et met les variables dans l'environnement.
load_dotenv()

# 📂 OÙ PLACER LE FICHIER .env ?
# À la RACINE du projet : agent_job_search/.env
# Exemple de contenu :
#   OPENAI_API_KEY=sk-proj-xxxxx
#   ADZUNA_APP_ID=cf2e9f9d
#   ADZUNA_APP_KEY=xxxxx


# ==============================================================
# 🔹 FONCTION DE SÉCURISATION
# ==============================================================

def get_env(key: str) -> str:
    """
    🎯 Récupère une variable d'environnement de façon sécurisée

    📚 EXPLICATION :
    Cette fonction essaie de récupérer la valeur d'une variable
    d'environnement. Si elle n'existe pas, elle lève une erreur
    EXPLICITE pour éviter que l'application ne tourne avec des
    configurations manquantes.

    Args:
        key: Le nom de la variable (ex: "OPENAI_API_KEY")

    Returns:
        str: La valeur de la variable

    Raises:
        ValueError: Si la variable n'est pas trouvée
    """

    value = os.getenv(key)

    # Vérification : si la variable n'existe pas ou est vide
    if not value:
        raise ValueError(f"❌ Variable d'environnement manquante : {key}")

    return value


# ==============================================================
# 🔹 CLASSE DE CONFIGURATION
# ==============================================================

class Settings:
    """
    🎯 Classe qui regroupe TOUTES les configurations de l'application

    📚 EXPLICATION :
    Cette classe contient toutes les variables de configuration.
    Chaque attribut est une constante qui définit le comportement
    de l'application.

    🏗️ ARCHITECTURE :
    - Les propriétés en MAJUSCULES sont des CONSTANTES
    - Les @property créent des alias (même valeur, nom différent)
    - Les chemins sont construits dynamiquement avec os.path.join()

    🔄 FLUX D'UTILISATION :
    Dans les autres fichiers, on fait :
        from app.core.config import settings
        api_key = settings.OPENAI_API_KEY
    """

    # ==========================================================
    # 🔑 API KEYS - LES PLUS IMPORTANTES (SENSIBLES)
    # ==========================================================

    # OpenAI : pour l'analyse IA et la génération de contenu
    # get_env() lève une erreur si la variable n'existe pas
    OPENAI_API_KEY: str = get_env("OPENAI_API_KEY")

    # Adzuna : pour récupérer les offres d'emploi
    ADZUNA_APP_ID: str = get_env("ADZUNA_APP_ID")      # Identifiant applicatif
    ADZUNA_APP_KEY: str = get_env("ADZUNA_APP_KEY")    # Clé secrète

    # ==========================================================
    # 🔹 ALIAS POUR COMPATIBILITÉ
    # ==========================================================

    @property
    def ADZUNA_API_KEY(self) -> str:
        """
        🎯 Alias pour ADZUNA_APP_KEY

        📚 EXPLICATION :
        Certains fichiers (comme adzuna_api.py) utilisent le nom
        ADZUNA_API_KEY. Cette propriété permet d'avoir les deux
        noms qui pointent vers la même valeur.

        C'est comme avoir deux portes d'entrée vers la même pièce.
        """
        return self.ADZUNA_APP_KEY

    # ==========================================================
    # 📂 CHEMINS DES FICHIERS
    # ==========================================================

    # BASE_DIR = dossier racine du projet (agent_job_search/)
    # os.path.dirname() remonte dans l'arborescence
    # On appelle 3 fois pour remonter de core/config.py à la racine
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    # Dossier data (contient les fichiers générés)
    DATA_DIR = os.path.join(BASE_DIR, "data")

    # Chemins spécifiques
    CV_PATH: str = os.path.join(DATA_DIR, "cv.pdf")                    # CV par défaut
    JOB_OFFERS_PATH: str = os.path.join(BASE_DIR, "job_offers.json")   # Offres sauvegardées
    APPLICATION_PACKS_PATH: str = os.path.join(BASE_DIR, "application_packs.json")  # Candidatures

    # Création automatique du dossier data s'il n'existe pas
    # exist_ok=True = ne pas générer d'erreur si le dossier existe déjà
    os.makedirs(DATA_DIR, exist_ok=True)

    # ==========================================================
    # 🤖 PARAMÈTRES IA (OpenAI)
    # ==========================================================

    # Modèle utilisé : gpt-4o-mini est économique et rapide
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Température : contrôle la créativité de l'IA
    # 0.0 = très précis, répétitif
    # 0.7 = équilibré
    # 1.0 = créatif, varié
    TEMPERATURE: float = 0.3   # Plutôt précis pour les analyses

    # Nombre maximum de tokens par réponse (1 token ≈ 0.75 mots)
    MAX_TOKENS: int = 1500

    # ==========================================================
    # 📊 SEUILS DE DÉCISION (MATCHING CV / OFFRE)
    # ==========================================================

    # Score minimum pour postuler automatiquement
    MATCH_THRESHOLD_APPLY: int = 75   # 75% = bon match

    # Score minimum pour examiner manuellement (entre 60 et 75)
    MATCH_THRESHOLD_REVIEW: int = 60  # 60% = à vérifier

    # ==========================================================
    # ⏱️ SCHEDULER (TÂCHES AUTOMATIQUES)
    # ==========================================================

    # Intervalle entre deux récupérations d'offres (en jours)
    FETCH_INTERVAL_DAYS: int = 2

    # Intervalle entre deux générations de candidatures (en jours)
    APPLY_INTERVAL_DAYS: int = 2

    # ==========================================================
    # 🌍 CRITÈRES DE RECHERCHE D'EMPLOI
    # ==========================================================

    # 🔥 MODIFIE CES VALEURS SELON TES BESOINS ! 🔥
    JOB_KEYWORD: str = "technicien production"   # ← Change par ton métier
    JOB_LOCATION: str = "Rennes"                 # ← Change par ta ville
    JOB_RESULTS_PER_PAGE: int = 20               # Offres par page
    JOB_MAX_PAGES: int = 3                      # Nombre de pages max


# ==============================================================
# 🔹 INSTANCE UNIQUE (SINGLETON)
# ==============================================================

# 📚 EXPLICATION :
# On crée une SEULE instance de Settings. C'est ce qu'on appelle
# un "singleton". Tous les fichiers qui importent 'settings'
# utilisent la MÊME instance, ce qui évite les duplications.
settings = Settings()


# ==============================================================
# 🔹 AFFICHAGE DE CONFIRMATION (AU DÉMARRAGE)
# ==============================================================

# 📚 EXPLICATION :
# Ces prints s'affichent quand l'application démarre.
# Ils permettent de vérifier que les clés API sont bien chargées.
# On ne montre que les premiers caractères pour des raisons de sécurité.

print("=" * 50)
print("🔧 CONFIGURATION CHARGÉE")
print("=" * 50)

# Affichage des clés (très partiel pour la sécurité)
print(f"🔑 OPENAI_API_KEY: {settings.OPENAI_API_KEY[:12]}... (OK)")

# Affichage complet de l'ID (peut être public)
print(f"📱 ADZUNA_APP_ID: {settings.ADZUNA_APP_ID}")

# Affichage partiel de la clé secrète
print(f"🔐 ADZUNA_APP_KEY: {settings.ADZUNA_APP_KEY[:8]}... (OK)")

print(f"📍 LOCALISATION: {settings.JOB_LOCATION}")
print(f"🔍 MOT-CLÉ: {settings.JOB_KEYWORD}")
print(f"🎯 SEUIL POSTULATION: {settings.MATCH_THRESHOLD_APPLY}%")
print(f"🤖 MODÈLE IA: {settings.OPENAI_MODEL}")
print("=" * 50)