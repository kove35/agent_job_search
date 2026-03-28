"""
=========================================================
📦 DATABASE CONFIGURATION - VERSION CORRIGÉE
=========================================================
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# ✅ Base de données à la racine du projet
DATABASE_URL = "sqlite:///./jobs.db"

# ✅ Création du moteur SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Nécessaire pour SQLite
)

# ✅ Création de la session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ LA SEULE BASE DU PROJET (c'est CETTE variable qui contient metadata)
Base = declarative_base()

# ✅ Fonction utilitaire pour créer les tables
def init_db():
    """Crée toutes les tables dans la base de données"""
    Base.metadata.create_all(bind=engine)
    print("✅ Base de données initialisée avec succès")

# Afficher le chemin de la DB pour debug
print("📍 DB ABSOLUE :", os.path.abspath("jobs.db"))