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
# Démarrage du scheduler (exécution périodique)
# ---------------------------------------------------------
start_scheduler()


# ---------------------------------------------------------
# Événement exécuté automatiquement au démarrage de FastAPI
# ---------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    """
    Cette fonction est exécutée UNE SEULE FOIS au démarrage du serveur.
    Elle lance immédiatement la récupération + analyse des offres.
    """
    print(">>> Lancement initial de fetch_and_store_job_offers()")
    fetch_and_store_job_offers()
