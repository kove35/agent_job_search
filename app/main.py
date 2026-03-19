# ---------------------------------------------------------
# Chargement des variables d'environnement (.env)
# ---------------------------------------------------------
from dotenv import load_dotenv
load_dotenv()


# ---------------------------------------------------------
# Import FastAPI et les routes
# ---------------------------------------------------------
from fastapi import FastAPI
from app.routers import profile, analyze, jobs, applications  # 🔥 ajout applications


# ---------------------------------------------------------
# Import du scheduler (tâches automatiques)
# ---------------------------------------------------------
from app.scheduler import start_scheduler


# ---------------------------------------------------------
# Import DATABASE (SQLite)
# ---------------------------------------------------------
from app.db.database import engine
from app.db.models import Base


# ---------------------------------------------------------
# Fonction de création de l'application FastAPI
# ---------------------------------------------------------
def create_app():
    """
    Initialise l'application FastAPI :
    - routes
    - base de données
    """

    app = FastAPI(
        title="Agent IA Recherche d'Emploi",
        version="0.2.0"
    )

    # -----------------------------------------------------
    # 🔥 Création des tables SQLite au démarrage
    # -----------------------------------------------------
    Base.metadata.create_all(bind=engine)

    # -----------------------------------------------------
    # Ajout des routes API
    # -----------------------------------------------------
    app.include_router(profile.router)
    app.include_router(analyze.router)
    app.include_router(jobs.router)
    app.include_router(applications.router)  # 🔥 nouvelle route

    return app


# ---------------------------------------------------------
# Création de l'application FastAPI utilisée par Uvicorn
# ---------------------------------------------------------
app = create_app()


# ---------------------------------------------------------
# Événement exécuté au démarrage
# ---------------------------------------------------------
@app.on_event("startup")
async def startup_event():

    print(">>> Démarrage de l'application")

    # -----------------------------------------------------
    # 1. Scheduler
    # -----------------------------------------------------
    try:
        print(">>> Démarrage du scheduler")
        start_scheduler()
    except Exception as e:
        print(f"❌ Erreur scheduler : {e}")

    # -----------------------------------------------------
    # 2. Info (fetch désactivé)
    # -----------------------------------------------------
    try:
        print(">>> Startup OK - mode dev")
    except Exception as e:
        print(f"❌ Erreur startup : {e}")