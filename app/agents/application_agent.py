from datetime import datetime

from app.services.ai_generator import generate_cover_letter
from app.services.cv_adapter import adapt_cv
from app.services.decision_engine import decide
from app.services.storage import save_application


def build_application(job: dict, cv_text: str):
    """
    Orchestre tout le processus
    """

    # 1️⃣ score
    score = job.get("matching_score", 0)

    # 2️⃣ décision
    decision = decide(score)

    # 3️⃣ adapter CV
    tailored_cv = adapt_cv(cv_text, job)

    # 4️⃣ lettre
    cover_letter = generate_cover_letter(job, cv_text)

    # 5️⃣ résultat
    result = {
        "job_id": job["id"],
        "title": job["title"],
        "company": job["company"],
        "decision": decision,
        "score": score,
        "cover_letter": cover_letter,
        "tailored_cv": tailored_cv,
        "created_at": datetime.utcnow()
    }

    # 6️⃣ sauvegarde
    save_application(result)

    return result