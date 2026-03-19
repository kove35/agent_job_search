# ---------------------------------------------------------
# Chargement des variables d'environnement (.env)
# ---------------------------------------------------------
from dotenv import load_dotenv
load_dotenv()

# ---------------------------------------------------------
# Import FastAPI et les routes
# ---------------------------------------------------------
from fastapi import FastAPI
from app.routers import profile, analyze, jobs

# ---------------------------------------------------------
# Import du scheduler (tâches automatiques)
# ---------------------------------------------------------
from app.scheduler import start_scheduler

# ---------------------------------------------------------
# Import de la fonction de récupération des offres
# ---------------------------------------------------------
from app.services.job_search import fetch_and_store_job_offers


# ---------------------------------------------------------
# Fonction de création de l'application FastAPI
# ---------------------------------------------------------
def create_app():
    """
    Initialise et configure l'application FastAPI.
    - Ajoute les routes
    - Définit le titre et la version
    """
    app = FastAPI(
        title="Agent IA Recherche d'Emploi",
        version="0.1.0"
    )

    # Ajout des routes API
    app.include_router(profile.router)
    app.include_router(analyze.router)
    app.include_router(jobs.router)

    return app


# ---------------------------------------------------------
# Création de l'application FastAPI utilisée par Uvicorn
# ---------------------------------------------------------
app = create_app()


# ---------------------------------------------------------
# Événement exécuté automatiquement au démarrage de FastAPI
# ---------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    """
    Cette fonction est exécutée une seule fois au démarrage du serveur.

    Elle :
    1. démarre le scheduler
    2. lance une récupération initiale des offres

    IMPORTANT :
    Si une erreur survient (OpenAI, Adzuna, etc.),
    on affiche l'erreur mais on ne bloque pas le démarrage de l'API.
    """
    print(">>> Démarrage de l'application")

    # 1. Lancer le scheduler
    try:
        print(">>> Démarrage du scheduler")
        start_scheduler()
    except Exception as e:
        print(f"❌ Erreur au démarrage du scheduler : {e}")

    # 2. Lancer le fetch initial
    try:
        print(">>> Startup OK - récupération des offres désactivée en mode développement")
    except Exception as e:
        print(f"❌ Erreur au démarrage lors du fetch/analyse des offres : {e}")