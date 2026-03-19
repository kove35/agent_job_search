from app.db.database import SessionLocal
from app.db.models import Application
from datetime import datetime


# =====================================================
# 🔹 SAVE APPLICATION
# =====================================================
def save_application(data: dict):
    """
    Sauvegarde en base SQLite (version robuste et propre)
    """

    db = SessionLocal()

    try:
        # validation minimale
        required_fields = ["job_id", "decision", "score"]

        for field in required_fields:
            if field not in data:
                raise ValueError(f"Champ manquant : {field}")

        # création objet
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

        print(f"✅ Application sauvegardée (ID={application.id})")

        return application.id

    except Exception as e:
        db.rollback()
        print(f"❌ Erreur DB : {e}")
        return None

    finally:
        db.close()


# =====================================================
# 🔹 GET APPLICATIONS (🔥 AJOUT IMPORTANT)
# =====================================================
def get_applications(
    decision: str = None,
    min_score: float = None,
    limit: int = 50
):
    """
    Récupère les candidatures avec filtres
    """

    db = SessionLocal()

    try:
        query = db.query(Application)

        # filtre décision
        if decision:
            query = query.filter(Application.decision == decision)

        # filtre score
        if min_score is not None:
            query = query.filter(Application.score >= min_score)

        # tri
        query = query.order_by(Application.score.desc())

        # limite
        query = query.limit(limit)

        applications = query.all()

        # conversion dict
        result = []
        for app in applications:
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