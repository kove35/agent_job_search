from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 🔹 fichier SQLite (créé automatiquement)
DATABASE_URL = "sqlite:///./jobs.db"

# 🔹 moteur de connexion
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # obligatoire pour SQLite
)

# 🔹 session = connexion à la DB
SessionLocal = sessionmaker(bind=engine)

# 🔹 base pour créer les tables
Base = declarative_base()