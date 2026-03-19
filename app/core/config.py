import os
from dotenv import load_dotenv

# ==========================================================
# CHARGEMENT .ENV
# ==========================================================
load_dotenv()


# ==========================================================
# FONCTION SÉCURISATION ENV
# ==========================================================
def get_env(key: str):
    value = os.getenv(key)
    if not value:
        raise ValueError(f"❌ Variable d'environnement manquante : {key}")
    return value


class Settings:
    # ==========================================================
    # 🔑 API KEYS
    # ==========================================================
    OPENAI_API_KEY: str = get_env("OPENAI_API_KEY")
    ADZUNA_APP_ID: str = get_env("ADZUNA_APP_ID")
    ADZUNA_APP_KEY: str = get_env("ADZUNA_APP_KEY")

    # ==========================================================
    # 📄 CHEMINS FICHIERS
    # ==========================================================
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    DATA_DIR = os.path.join(BASE_DIR, "data")

    CV_PATH: str = os.path.join(DATA_DIR, "cv.pdf")
    JOB_OFFERS_PATH: str = os.path.join(BASE_DIR, "job_offers.json")
    APPLICATION_PACKS_PATH: str = os.path.join(BASE_DIR, "application_packs.json")

    # Création automatique du dossier data
    os.makedirs(DATA_DIR, exist_ok=True)

    # ==========================================================
    # ⚙️ PARAMÈTRES IA
    # ==========================================================
    OPENAI_MODEL: str = "gpt-4o-mini"
    TEMPERATURE: float = 0.3
    MAX_TOKENS: int = 1500

    # ==========================================================
    # 📊 MATCHING / DÉCISION
    # ==========================================================
    MATCH_THRESHOLD_APPLY: int = 75
    MATCH_THRESHOLD_REVIEW: int = 60

    # ==========================================================
    # ⏱️ SCHEDULER
    # ==========================================================
    FETCH_INTERVAL_DAYS: int = 2
    APPLY_INTERVAL_DAYS: int = 2

    # ==========================================================
    # 🌍 RECHERCHE EMPLOI
    # ==========================================================
    JOB_KEYWORD: str = "technicien production"
    JOB_LOCATION: str = "Rennes"
    JOB_RESULTS_PER_PAGE: int = 20
    JOB_MAX_PAGES: int = 3


# Instance globale
settings = Settings()

print("OPENAI_API_KEY chargée =", settings.OPENAI_API_KEY[:12], "...")
print("ADZUNA_APP_ID chargée =", settings.ADZUNA_APP_ID)