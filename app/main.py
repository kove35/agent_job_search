from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.routers import profile, analyze, jobs, applications
from app.routers.agents import router as agent_router

# ✅ DB
from app.db.database import engine, Base
from app.db.database import engine
print(engine)
from app.db.database import engine
print(engine)
# 🔥 IMPORTANT : charger les modèles
import app.db.models

# scheduler
from app.scheduler import start_scheduler


# =========================================================
# 🔥 CREATE TABLES
# =========================================================

metadata = Base.metadata  # Méthode 2
metadata.create_all(bind=engine)
# ---------------------------------------------------------
# Fonction de création de l'application FastAPI
# ---------------------------------------------------------
def create_app():
    """
    Initialise l'application FastAPI :
    - routes
    - base de données
    """

    # -----------------------------------------------------
    # 🔥 NOUVEAU : Gestionnaire de cycle de vie
    # -----------------------------------------------------
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # ----- STARTUP -----
        print(">>> Démarrage de l'application")
        
        # 1. Scheduler
        try:
            print(">>> Démarrage du scheduler")
            start_scheduler()
        except Exception as e:
            print(f"❌ Erreur scheduler : {e}")
        
        # 2. Info (fetch désactivé)
        try:
            print(">>> Startup OK - mode dev")
        except Exception as e:
            print(f"❌ Erreur startup : {e}")
        
        yield  # L'application tourne ici
        
        # ----- SHUTDOWN (optionnel) -----
        print(">>> Arrêt de l'application")
        # Ajoute ici du code de nettoyage si nécessaire (ex: fermeture du scheduler)

    app = FastAPI(
        title="Agent IA Recherche d'Emploi",
        version="0.2.0",
        lifespan=lifespan  # 🔥 NOUVEAU : on passe le gestionnaire de cycle de vie
    )

    # -----------------------------------------------------
    # 🔥 Création des tables SQLite au démarrage
    # -----------------------------------------------------
 
    # -----------------------------------------------------
    # Ajout des routes API
    # -----------------------------------------------------
    app.include_router(profile.router)
    app.include_router(analyze.router)
    app.include_router(jobs.router)
    app.include_router(applications.router)
    app.include_router(agent_router)
    
    return app


# ---------------------------------------------------------
# Création de l'application FastAPI utilisée par Uvicorn
# ---------------------------------------------------------
app = create_app()