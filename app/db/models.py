from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


# =========================================================
# 🔹 USERS (NOUVEAU - IMPORTANT)
# =========================================================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("UserProfileDB", back_populates="user", uselist=False)
    applications = relationship("Application", back_populates="user")


# =========================================================
# 🔹 PROFIL UTILISATEUR
# =========================================================
class UserProfileDB(Base):
    __tablename__ = "user_profile"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    skills = Column(JSON)
    job_targets = Column(JSON)
    experience_level = Column(String)
    remote_only = Column(Boolean)
    locations = Column(JSON)
    salary_min = Column(Integer)
    avoid_keywords = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="profile")


# =========================================================
# 🔹 JOBS (NOUVEAU - CRITIQUE)
# =========================================================
class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String)
    company = Column(String)
    description = Column(String)
    location = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)


# =========================================================
# 🔹 APPLICATIONS
# =========================================================
class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))

    score = Column(Float)
    decision = Column(String)

    cover_letter = Column(String)
    tailored_cv = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="applications")
    job = relationship("Job")