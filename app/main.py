"""
=====================================================================
🚀 MAIN APPLICATION - FASTAPI
=====================================================================

🎯 RÔLE :
Point d'entrée principal de l'application. C'est ce fichier que
Uvicorn exécute pour démarrer le serveur.

📚 POUR UN DÉBUTANT :
- Ce fichier crée l'application FastAPI
- Il enregistre toutes les routes (API endpoints)
- Il initialise la base de données
- Il démarre le scheduler pour les tâches automatiques

=====================================================================
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager

# ==============================================================
# 🔹 IMPORTS DES ROUTES (les endpoints de l'API)
# ==============================================================
from app.routers import profile, analyze, jobs, applications
from app.routers.agents import router as agent_router
from app.routers import cv_optimization  # ✅ Router pour l'optimisation du CV

# ==============================================================
# 🔹 BASE DE DONNÉES
# ==============================================================
from app.db.database import engine, Base, init_db  # ✅ Ajout de init_db

# 🔥 IMPORTANT : Charger les modèles pour que SQLAlchemy les connaisse
# Sans cet import, les tables ne seront pas créées automatiquement
import app.db.models

# ==============================================================
# 🔹 SCHEDULER (tâches automatiques)
# ==============================================================
from app.scheduler import start_scheduler

# ==============================================================
# 🔹 LOGGING
# ==============================================================
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==============================================================
# 🔹 FONCTION DE CRÉATION DE L'APPLICATION
# ==============================================================

def create_app() -> FastAPI:
    """
    🎯 Crée et configure l'application FastAPI

    📚 POUR UN DÉBUTANT :
    Cette fonction est appelée une fois au démarrage. Elle :
    1. Crée l'application FastAPI
    2. Configure le cycle de vie (lifespan) : ce qui se passe au démarrage et à l'arrêt
    3. Enregistre toutes les routes (API endpoints)
    4. Retourne l'application prête à être utilisée

    Returns:
        FastAPI: L'application configurée
    """

    # ==========================================================
    # 🔥 GESTIONNAIRE DE CYCLE DE VIE (lifespan)
    # ==========================================================
    # 📚 POUR UN DÉBUTANT :
    # Le lifespan permet d'exécuter du code :
    # - AVANT que l'API ne démarre (startup)
    # - APRÈS que l'API s'arrête (shutdown)
    # C'est l'endroit idéal pour initialiser la DB et démarrer le scheduler

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # ======================================================
        # 🔥 STARTUP - Code exécuté AVANT le démarrage de l'API
        # ======================================================
        print("=" * 50)
        print("🚀 DÉMARRAGE DE L'APPLICATION")
        print("=" * 50)

        # 1️⃣ INITIALISATION DE LA BASE DE DONNÉES
        print("📦 Initialisation de la base de données...")
        try:
            # Méthode 1 : Utiliser la fonction init_db (recommandée)
            init_db()
            print("✅ Base de données initialisée avec succès")
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation de la DB : {e}")

        # 2️⃣ DÉMARRAGE DU SCHEDULER (tâches automatiques)
        print("⏰ Démarrage du scheduler...")
        try:
            start_scheduler()
            print("✅ Scheduler démarré avec succès")
        except Exception as e:
            print(f"❌ Erreur lors du démarrage du scheduler : {e}")

        # 3️⃣ AFFICHAGE DES INFOS DE DÉMARRAGE
        print("=" * 50)
        print("✅ APPLICATION PRÊTE")
        print("📡 API disponible sur http://127.0.0.1:8000")
        print("📚 Documentation: http://127.0.0.1:8000/docs")
        print("=" * 50)

        # ======================================================
        # 🔥 L'APPLICATION TOURNE ICI
        # ======================================================
        yield  # C'est ici que l'API est active

        # ======================================================
        # 🔥 SHUTDOWN - Code exécuté APRÈS l'arrêt de l'API
        # ======================================================
        print("=" * 50)
        print("🛑 ARRÊT DE L'APPLICATION")
        print("=" * 50)
        
        # Ajouter ici du code de nettoyage si nécessaire :
        # - Fermeture des connexions DB
        # - Arrêt propre du scheduler
        # - Sauvegarde des données en mémoire
        print("✅ Nettoyage terminé")

    # ==========================================================
    # 🔥 CRÉATION DE L'APPLICATION FASTAPI
    # ==========================================================
    app = FastAPI(
        title="Agent IA Recherche d'Emploi",
        description="""
        🤖 Agent IA pour automatiser la recherche d'emploi et la génération de candidatures.
        
        ## Fonctionnalités :
        - Récupération automatique d'offres (API Adzuna)
        - Analyse IA du CV et des offres
        - Matching CV ↔ Offre avec scoring
        - Génération de lettres de motivation personnalisées
        - Optimisation du CV par offre
        - Dashboard Streamlit pour visualiser les candidatures
        
        ## Endpoints principaux :
        - `/agent/run` : Lance l'agent IA pour analyser les offres
        - `/agent/apply` : Génère une candidature pour une offre
        - `/cv/list` : Liste des CV disponibles
        - `/cv/upload` : Upload d'un nouveau CV
        - `/cv/delete` : Suppression d'un CV
        - `/cv/optimize` : Optimisation du CV pour une offre spécifique
        - `/applications` : Historique des candidatures
        """,
        version="0.2.0",
        lifespan=lifespan  # 🔥 On attache le gestionnaire de cycle de vie
    )

    # ==========================================================
    # 🔥 ENREGISTREMENT DES ROUTES (API ENDPOINTS)
    # ==========================================================
    # 📚 POUR UN DÉBUTANT :
    # Chaque router contient un groupe d'endpoints :
    # - /profile   → gestion du profil utilisateur
    # - /analyze   → analyse CV et offres
    # - /jobs      → recherche et gestion des offres
    # - /applications → gestion des candidatures
    # - /agent     → agent IA autonome
    # - /cv        → gestion et optimisation des CV

    # Routes de gestion du profil
    app.include_router(profile.router, prefix="/profile", tags=["Profile"])
    
    # Routes d'analyse (CV, offres)
    app.include_router(analyze.router, prefix="/analyze", tags=["Analyze"])
    
    # Routes de recherche d'offres
    app.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
    
    # Routes de gestion des candidatures
    app.include_router(applications.router, prefix="/applications", tags=["Applications"])
    
    # Routes de l'agent IA (run, apply)
    app.include_router(agent_router, prefix="/agent", tags=["Agent"])
    
    # ✅ Routes de gestion et optimisation des CV (list, upload, delete, optimize)
    # Le router cv_optimization a déjà son propre prefix="/cv"
    app.include_router(cv_optimization.router, tags=["CV Management"])

    # ==========================================================
    # 🔥 AFFICHAGE DES ROUTES ENREGISTRÉES (DEBUG)
    # ==========================================================
    print("\n📋 ROUTES ENREGISTRÉES:")
    for route in app.routes:
        # Afficher seulement les routes API (pas les routes statiques)
        if hasattr(route, "path"):
            methods = getattr(route, "methods", set())
            if methods:
                print(f"   {', '.join(methods)} {route.path}")
    print("")

    # ==========================================================
    # 🔥 ENDPOINT DE TEST (vérifier que l'API fonctionne)
    # ==========================================================
    @app.get("/")
    async def root():
        """
        Endpoint racine pour vérifier que l'API est en ligne
        
        Returns:
            dict: Informations sur l'API
        """
        return {
            "status": "online",
            "message": "🤖 Agent IA Recherche d'Emploi",
            "version": "0.2.0",
            "docs": "/docs",
            "endpoints": {
                "agent": "/agent/run",
                "cv_list": "/cv/list",
                "cv_optimize": "/cv/optimize",
                "applications": "/applications"
            }
        }

    @app.get("/health")
    async def health_check():
        """
        Endpoint de santé pour les monitoring (Docker, Kubernetes, etc.)
        
        Returns:
            dict: Statut de l'application et de ses dépendances
        """
        health_status = {
            "status": "healthy",
            "database": "connected",
            "scheduler": "running"
        }
        
        # Vérifier la connexion à la base de données
        try:
            from app.db.database import SessionLocal
            db = SessionLocal()
            db.execute("SELECT 1")
            db.close()
            health_status["database"] = "connected"
        except Exception as e:
            health_status["database"] = f"error: {str(e)}"
            health_status["status"] = "degraded"
        
        return health_status

    return app


# ==============================================================
# 🔥 CRÉATION DE L'INSTANCE PRINCIPALE
# ==============================================================
# 📚 POUR UN DÉBUTANT :
# Cette ligne crée l'application que Uvicorn va utiliser.
# Uvicorn cherche une variable 'app' dans ce fichier.

app = create_app()


# ==============================================================
# 🔥 POUR LANCER L'APPLICATION EN LOCAL (DEVELOPPEMENT)
# ==============================================================
# Si vous exécutez ce fichier directement (python app/main.py)
# Uvicorn démarre automatiquement le serveur

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 50)
    print("🚀 DÉMARRAGE DU SERVEUR DE DÉVELOPPEMENT")
    print("=" * 50)
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,          # Mode développement : rechargement automatique
        log_level="info",     # Niveau de logs
        access_log=True       # Afficher les requêtes HTTP
    )