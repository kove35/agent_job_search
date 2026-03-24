from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./jobs.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)

# ✅ LA SEULE BASE DU PROJET
Base = declarative_base()
import os
print("📍 DB ABSOLUE :", os.path.abspath("jobs.db"))