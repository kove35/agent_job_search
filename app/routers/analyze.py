# =========================================================
# 📦 ROUTER ANALYZE (VERSION PROFESSIONNELLE COMMENTÉE)
# =========================================================
"""
🎯 RÔLE DU FICHIER :
-------------------
Ce router expose toutes les fonctionnalités IA via FastAPI.

Il permet :
✔ analyser une offre
✔ analyser un CV
✔ matcher CV ↔ offre
✔ optimiser un CV
✔ générer une lettre
✔ extraire un CV PDF
✔ récupérer les jobs

👉 C’est la couche API entre ton frontend (ou Swagger)
   et ton moteur IA (ai_agent.py)
"""

# =========================================================
# 🔹 IMPORTS STANDARD
# =========================================================
from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel
from typing import List
import json
from app.agents.autonomous_agent import run_autonomous_agent
from fastapi import UploadFile, File
import shutil

# =========================================================
# 🔹 IMPORTS SERVICES IA
# =========================================================
"""
👉 Ces fonctions contiennent toute l’intelligence GPT.
👉 Le router ne fait que les appeler.
"""
from app.services.ai_agent import (
    analyze_offer,            # analyse une offre
    analyze_cv,               # analyse un CV
    match_cv_offer,           # compare CV ↔ offre
    optimize_cv_for_offer,    # optimise CV
    score_analysis,           # scoring détaillé
    auto_apply,               # pipeline complet IA
    clean_cv_text             # nettoyage texte CV
)


# =========================================================
# 🔹 IMPORTS EXTRACTION PDF
# =========================================================
"""
👉 Séparation claire :
- PDF → cv_extraction.py
- IA → ai_agent.py
"""
from app.services.cv_extraction import extract_text_from_pdf


# =========================================================
# 🔹 IMPORT JOBS
# =========================================================
from app.services.job_search import fetch_and_store_job_offers
from app.models.job import AnalyzedJob


# =========================================================
# 🔹 INITIALISATION ROUTER
# =========================================================
"""
👉 Tous les endpoints définis ici seront accessibles via /analyze/...
"""
router = APIRouter()


# =========================================================
# 🔹 MODELES DE DONNÉES (Pydantic)
# =========================================================
"""
👉 Ces classes définissent la structure attendue
👉 Elles sécurisent les entrées API
"""

class Offer(BaseModel):
    title: str
    description: str
    location: str


class CV(BaseModel):
    text: str


class MatchRequest(BaseModel):
    cv: dict
    offer: dict


class OptimizeRequest(BaseModel):
    cv: dict
    offer: dict
    match: dict


class ScoreRequest(BaseModel):
    cv: dict
    offer: dict


class AutoApplyRequest(BaseModel):
    cv_text: str
    offer: dict


# =========================================================
# 🔹 ENDPOINT : ANALYSE OFFRE
# =========================================================
@router.post("/analyze")
def analyze_job_offer(offer: Offer):
    """
    Analyse une offre d'emploi.

    INPUT :
    - titre
    - description
    - localisation

    OUTPUT :
    - résumé
    - compétences
    - niveau
    - recommandations
    """
    return analyze_offer(offer)


# =========================================================
# 🔹 ENDPOINT : ANALYSE CV TEXTE
# =========================================================
@router.post("/analyze_cv")
def analyze_cv_endpoint(cv: CV):
    """
    Analyse un CV (texte brut).

    Étapes :
    1. Nettoyage du texte
    2. Envoi à GPT
    3. Retour structuré
    """
    cleaned = clean_cv_text(cv.text)
    return analyze_cv(cleaned)


# =========================================================
# 🔹 ENDPOINT : MATCH CV ↔ OFFRE
# =========================================================
@router.post("/match")
def match_endpoint(data: MatchRequest):
    """
    Compare un CV et une offre.

    OUTPUT :
    - score de matching
    - compétences manquantes
    - points forts
    """
    return match_cv_offer(data.cv, data.offer)


# =========================================================
# 🔹 ENDPOINT : OPTIMISATION CV
# =========================================================
@router.post("/optimize_cv")
def optimize_cv_endpoint(data: OptimizeRequest):
    """
    Génère une version optimisée du CV.

    INPUT :
    - analyse CV
    - analyse offre
    - résultat du matching

    OUTPUT :
    - CV amélioré
    """
    return optimize_cv_for_offer(data.cv, data.offer, data.match)


# =========================================================
# 🔹 ENDPOINT : SCORING DÉTAILLÉ
# =========================================================
@router.post("/score")
def score_endpoint(data: ScoreRequest):
    """
    Génère un score détaillé (technique, soft skills, etc.)
    """
    return score_analysis(data.cv, data.offer)


# =========================================================
# 🔹 ENDPOINT : AUTO APPLY (FULL IA)
# =========================================================
@router.post("/auto_apply")
def auto_apply_endpoint(data: AutoApplyRequest):
    """
    Pipeline complet IA en une seule requête.

    Génère :
    - analyse CV
    - analyse offre
    - matching
    - CV optimisé
    - lettre de motivation
    """
    return auto_apply(data.cv_text, data.offer)


# =========================================================
# 🔹 ENDPOINT : EXTRACTION CV PDF
# =========================================================
@router.post("/extract_cv")
async def extract_cv_endpoint(file: UploadFile = File(...)):
    """
    Upload un PDF → retourne texte propre

    Étapes :
    1. Sauvegarde temporaire
    2. Extraction texte
    3. Nettoyage
    """

    try:
        # 📁 Sauvegarde temporaire du fichier
        temp_path = "temp_cv.pdf"

        with open(temp_path, "wb") as f:
            f.write(await file.read())

        # 📄 Extraction du texte depuis le PDF
        text = extract_text_from_pdf(temp_path)

        # 🧹 Nettoyage du texte
        cleaned = clean_cv_text(text)

        return {"text": cleaned}

    except Exception as e:
        return {"error": str(e)}


# =========================================================
# 🔹 ENDPOINT : LISTE DES JOBS
# =========================================================
from app.db.database import SessionLocal
from app.db.models import Job
@router.get("/job_suggestions")
def job_suggestions():

    db = SessionLocal()

    jobs = db.query(Job).order_by(Job.id.desc()).limit(50).all()

    result = [
        {
            "id": j.id,
            "title": j.title,
            "company": j.company,
            "description": j.description,
            "location": j.location
        }
        for j in jobs
    ]

    db.close()

    return result

# =========================================================
# 🔹 ENDPOINT : REFRESH JOBS
# =========================================================
@router.get("/refresh_jobs")
def refresh_jobs():
    """
    Relance la récupération des offres via Adzuna
    """
    fetch_and_store_job_offers()
    return {
        "status": "OK",
        "message": "Offres mises à jour"
    }
    
from app.db.database import SessionLocal
from app.db.models import Job

@router.get("/debug_add_job")
def debug_add_job():

    db = SessionLocal()

    job = Job(
        title="Technicien maintenance",
        company="Renault",
        description="Maintenance industrielle",
        location="Rennes"
    )

    db.add(job)
    db.commit()
    db.close()

    return {"status": "job ajouté"}


@router.post("/agent/run")
async def run_agent(file: UploadFile = File(...), min_score: int = 10):

    # =========================
    # 🔥 1. SAVE TEMP FILE
    # =========================
    file_path = f"temp_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    print("📄 CV sauvegardé :", file_path)

    # =========================
    # 🔥 2. RUN AGENT
    # =========================
    profile = {
        "skills": ["production", "maintenance", "industrie"],
        "job_targets": ["technicien"],
        "locations": ["rennes"],
        "remote_only": False,
        "avoid_keywords": []
    }

    results = run_autonomous_agent(
        cv_pdf_path=file_path,
        profile=profile
    )

    return {
        "status": "agent exécuté",
        "results": results
    }