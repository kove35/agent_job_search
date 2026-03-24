# =========================================================
# 📦 APPLICATION STORAGE (DATABASE LAYER)
# =========================================================
# 🧱 RÔLE :
# ----------
# Gérer UNIQUEMENT les candidatures en base de données
#
# 👉 Responsabilités :
# - sauvegarder une candidature
# - lire les candidatures
#
# ❌ NE FAIT PAS :
# - fichiers CV
# - IA
# - API
#
# 👉 Pattern :
# DATA ACCESS LAYER (DAL)
#
# =========================================================

from app.db.database import SessionLocal
from app.db.models import Application
from datetime import datetime


# =========================================================
# 💾 SAVE APPLICATION
# =========================================================
def save_application(data: dict):
    """
    🎯 OBJECTIF :
    Sauvegarder une candidature en DB

    🧠 ALGO :
    ----------
    1. ouvrir session DB
    2. créer objet Application
    3. ajouter
    4. commit
    5. retourner ID

    ⚠️ IMPORTANT :
    - ne fait PAS de logique IA
    - pure écriture DB
    """

    db = SessionLocal()

    try:
        application = Application(
            job_id=data["job_id"],
            title=data.get("title"),
            company=data.get("company"),
            decision=data["decision"],
            score=data["score"],
            cover_letter=data.get("cover_letter"),
            tailored_cv=data.get("tailored_cv"),
            created_at=datetime.utcnow()
        )

        db.add(application)
        db.commit()
        db.refresh(application)

        return application.id

    except Exception as e:
        db.rollback()
        print(f"❌ Erreur DB : {e}")
        return None

    finally:
        db.close()


# =========================================================
# 📊 GET APPLICATIONS
# =========================================================
def get_applications():
    """
    🎯 OBJECTIF :
    Lire les candidatures depuis la DB

    🧠 ALGO :
    ----------
    1. ouvrir session
    2. query DB
    3. transformer en dict
    4. retourner liste

    ⚠️ IMPORTANT :
    - ne retourne PAS objets SQLAlchemy
    - retourne JSON propre pour API
    """

    db = SessionLocal()

    try:
        apps = db.query(Application).all()

        result = []

        for app in apps:
            result.append({
                "id": app.id,
                "job_id": app.job_id,
                "title": app.title,
                "company": app.company,
                "decision": app.decision,
                "score": app.score,
                "created_at": app.created_at
            })

        return result

    finally:
        db.close()