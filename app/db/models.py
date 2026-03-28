"""
=====================================================================
📦 MODÈLES SQLALCHEMY - VERSION BASE DE DONNÉES
=====================================================================

🎯 QU'EST-CE QUE CE FICHIER ?
--------------------------------------------------------------------------------
Ce fichier définit la STRUCTURE de votre base de données.
Chaque classe = une table SQL.

📚 POUR UN DÉBUTANT :
- Une classe = une table
- Un attribut = une colonne
- Une relation = comment les tables sont connectées

=====================================================================
"""

# =====================================================================
# 🔹 IMPORTS
# =====================================================================
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
# ✅ IMPORT CORRECT : on importe Base depuis database.py
from app.db.database import Base



# =====================================================================
# 🔹 TABLE USERS (LES UTILISATEURS)
# =====================================================================
class User(Base):
    """
    Table "users" : chaque ligne = un utilisateur de l'application
    
    🏗️ RÔLE : Gérer l'authentification et l'identification
    """

    __tablename__ = "users"

    # 🔑 Identifiant unique
    id = Column(Integer, primary_key=True, index=True)
    
    # 📧 Informations de connexion
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    
    # 🔐 Authentification (à ajouter plus tard)
    # hashed_password = Column(String, nullable=True)
    
    # 📅 Dates
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 🔗 RELATIONS
    # Un utilisateur a UN profil
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    # Un utilisateur a PLUSIEURS candidatures
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")


# =====================================================================
# 🔹 TABLE USER_PROFILE (LE PROFIL DE L'UTILISATEUR)
# =====================================================================
class UserProfile(Base):
    """
    Table "user_profiles" : chaque ligne = le profil d'un utilisateur
    
    🏗️ RÔLE : Stocker le CV analysé et les préférences de l'utilisateur
    """

    __tablename__ = "user_profiles"

    # 🔑 Identifiant unique
    id = Column(Integer, primary_key=True, index=True)
    
    # 🔗 Lien vers l'utilisateur (1-1)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    # ==============================================================
    # 📋 DONNÉES EXTRAITES DU CV (par l'IA)
    # ==============================================================
    
    # Compétences techniques
    skills = Column(JSON, default=list)  # Ex: ["Python", "JavaScript", "React"]
    
    # Compétences comportementales
    soft_skills = Column(JSON, default=list)  # Ex: ["Teamwork", "Communication"]
    
    # Types de postes recherchés
    job_targets = Column(JSON, default=list)  # Ex: ["Data Scientist", "AI Engineer"]
    
    # Niveau d'expérience
    experience_level = Column(String, default="junior")  # junior, confirmé, senior
    
    # Années d'expérience
    years_experience = Column(Float, default=0)
    
    # Préférences
    remote_only = Column(Boolean, default=False)
    locations = Column(JSON, default=list)  # Ex: ["Paris", "Lyon", "Remote"]
    salary_min = Column(Integer, nullable=True)
    avoid_keywords = Column(JSON, default=list)  # Mots à éviter dans les offres

    # ==============================================================
    # 📋 STOCKAGE DU CV (pour réutilisation)
    # ==============================================================
    
    # Fichier PDF original
    cv_filename = Column(String, nullable=True)  # Ex: "jean_dupont_cv.pdf"
    
    # Texte extrait du PDF
    cv_text = Column(Text, nullable=True)
    
    # Analyse complète de l'IA (stockée en JSON)
    cv_analysis = Column(JSON, nullable=True)  # {resume, hard_skills, soft_skills, ...}

    # ==============================================================
    # 📋 MÉTADONNÉES
    # ==============================================================
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 🔗 RELATIONS
    user = relationship("User", back_populates="profile")


# =====================================================================
# 🔹 TABLE JOBS (LES OFFRES D'EMPLOI)
# =====================================================================
class Job(Base):
    """
    Table "jobs" : chaque ligne = une offre d'emploi
    
    🏗️ RÔLE : Stocker les offres récupérées de l'API Adzuna
    """

    __tablename__ = "jobs"

    # 🔑 Identifiant unique
    id = Column(Integer, primary_key=True, index=True)
    
    # 🔗 ID externe (Adzuna)
    external_id = Column(String, index=True, nullable=True)

    # ==============================================================
    # 📋 INFORMATIONS DE BASE
    # ==============================================================
    
    title = Column(String, nullable=False)       # Titre du poste
    company = Column(String, nullable=True)      # Nom de l'entreprise
    description = Column(Text, nullable=True)    # Description complète
    location = Column(String, nullable=True)     # Localisation

    # ==============================================================
    # 📋 INFORMATIONS COMPLÉMENTAIRES
    # ==============================================================
    
    url = Column(String, nullable=True)          # URL de l'offre originale
    salary = Column(String, nullable=True)       # Salaire (texte libre)
    contract_type = Column(String, nullable=True) # CDI, CDD, Stage, Freelance
    
    # ==============================================================
    # 📋 ANALYSE IA DE L'OFFRE
    # ==============================================================
    
    # Analyse complète par l'IA (stockée en JSON)
    job_analysis = Column(JSON, nullable=True)   # {resume, hard_skills, soft_skills, ...}

    # ==============================================================
    # 📋 MÉTADONNÉES
    # ==============================================================
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 🔗 RELATIONS
    # Une offre peut avoir plusieurs candidatures
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")


# =====================================================================
# 🔹 TABLE APPLICATIONS (LES CANDIDATURES GÉNÉRÉES)
# =====================================================================
class Application(Base):
    """
    Table "applications" : chaque ligne = une candidature générée
    
    🏗️ RÔLE : Centraliser les candidatures (table de jointure entre User et Job)
    """

    __tablename__ = "applications"

    # 🔑 Identifiant unique
    id = Column(Integer, primary_key=True, index=True)

    # ==============================================================
    # 📋 CLÉS ÉTRANGÈRES (liens vers les autres tables)
    # ==============================================================
    
    # Quel utilisateur a postulé ?
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # À quelle offre a-t-il postulé ?
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)

    # ==============================================================
    # 📋 RÉSULTATS DU MATCHING (CV vs OFFRE)
    # ==============================================================
    
    # Score global de compatibilité (0-100)
    score = Column(Float, default=0)
    
    # Score technique (compétences)
    technical_score = Column(Float, default=0)
    
    # Score d'expérience
    experience_score = Column(Float, default=0)
    
    # Score sémantique (mots-clés)
    semantic_score = Column(Float, default=0)
    
    # ==============================================================
    # 📋 DÉCISION DE L'AGENT
    # ==============================================================
    
    # Décision finale : "apply", "skip", "pending"
    decision = Column(String, default="pending")
    
    # Compétences manquantes (pour diagnostic)
    missing_skills = Column(JSON, default=list)
    
    # Points forts identifiés
    strengths = Column(JSON, default=list)

    # ==============================================================
    # 📋 DOCUMENTS GÉNÉRÉS
    # ==============================================================
    
    # Lettre de motivation générée par l'IA
    cover_letter = Column(Text, nullable=True)
    
    # Chemin vers le CV optimisé pour cette offre
    # Ex: "storage/cv/jean_dupont_optimized_data_analyst.pdf"
    optimized_cv_path = Column(String, nullable=True)
    
    # Chemin vers la lettre de motivation en PDF
    cover_letter_pdf_path = Column(String, nullable=True)

    # ==============================================================
    # 📋 STATUT DE LA CANDIDATURE
    # ==============================================================
    
    # Statut : "draft", "sent", "accepted", "rejected", "archived"
    status = Column(String, default="draft")

    # ==============================================================
    # 📋 MÉTADONNÉES
    # ==============================================================
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)  # Date d'envoi de la candidature

    # 🔗 RELATIONS
    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")


# =====================================================================
# 🔹 TABLE MATCHING_HISTORY (OPTIONNELLE - POUR LE SUIVI)
# =====================================================================
class MatchingHistory(Base):
    """
    Table "matching_history" : historique des matchings effectués
    
    🏗️ RÔLE : Stocker l'historique des comparaisons CV/Offre pour analyse
    
    📚 POUR UN DÉBUTANT :
    Cette table est optionnelle mais utile pour :
    - Analyser les performances de l'algorithme de matching
    - Comprendre pourquoi une offre a été acceptée ou refusée
    - Améliorer le système avec des données réelles
    """

    __tablename__ = "matching_history"

    id = Column(Integer, primary_key=True, index=True)
    
    # Liens
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"))
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="SET NULL"), nullable=True)
    
    # Résultats du matching
    score = Column(Float, default=0)
    decision = Column(String)  # apply, skip
    
    # Détails (stockés en JSON pour analyse)
    match_details = Column(JSON, nullable=True)  # {skills_score, semantic_score, ...}
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)


# =====================================================================
# 📊 SCHÉMA COMPLET DE LA BASE DE DONNÉES
# =====================================================================
"""
                    ┌─────────────────────────────────────────────────────────┐
                    │                      users                              │
                    │  ┌─────────┐  ┌─────────┐  ┌─────────────────────┐    │
                    │  │ id (PK) │  │ email   │  │ name                │    │
                    │  └─────────┘  └─────────┘  └─────────────────────┘    │
                    └──────┬──────────────┬──────────────────────────────────┘
                           │              │
                           │ 1            │ 1
                           ▼              ▼
        ┌──────────────────────────┐  ┌──────────────────────────────────────┐
        │     user_profiles        │  │          applications                │
        │  ┌────────────────────┐  │  │  ┌─────────┐  ┌─────────────────┐  │
        │  │ user_id (FK)       │  │  │  │ user_id │  │ job_id (FK)     │  │
        │  │ skills (JSON)      │  │  │  │ score   │  │ cover_letter    │  │
        │  │ cv_filename        │  │  │  │ status  │  │ optimized_cv_path│  │
        │  │ cv_analysis (JSON) │  │  │  └─────────┘  └─────────────────┘  │
        │  └────────────────────┘  │  └──────────────────────────────────────┘
        └──────────────────────────┘                     │
                                                         │
                                                         │ n
                                                         ▼
                                    ┌──────────────────────────────────────────┐
                                    │                 jobs                     │
                                    │  ┌─────────┐  ┌─────────────────────┐    │
                                    │  │ id (PK) │  │ title               │    │
                                    │  │ company │  │ description         │    │
                                    │  │ location│  │ job_analysis (JSON) │    │
                                    │  └─────────┘  └─────────────────────┘    │
                                    └──────────────────────────────────────────┘

🔑 LÉGENDE :
- (PK) = Primary Key (clé primaire)
- (FK) = Foreign Key (clé étrangère)
- JSON = colonne qui stocke des données structurées
- 1 = relation un-à-un
- n = relation un-à-plusieurs
"""

