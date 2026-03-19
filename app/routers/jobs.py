from fastapi import APIRouter
import json
import os

from app.core.config import settings
from app.services.job_search import fetch_and_store_job_offers

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)


# ---------------------------------------------------------
# 🚀 ROUTE : RAFRAÎCHIR LES OFFRES
# ---------------------------------------------------------
@router.get("/fetch")
def fetch_jobs(max_pages: int = 1, results_per_page: int = 3):
    """
    Lance la récupération + analyse des offres.

    Paramètres :
    - max_pages : nombre de pages Adzuna
    - results_per_page : nombre d'offres par page
    """
    try:
        fetch_and_store_job_offers(
            max_pages=max_pages,
            results_per_page=results_per_page
        )

        return {
            "status": "success",
            "message": f"Offres récupérées (pages={max_pages}, results={results_per_page})"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# ---------------------------------------------------------
# 📄 ROUTE : LIRE LES OFFRES STOCKÉES
# ---------------------------------------------------------
@router.get("/")
def get_jobs(min_score: int = 0, decision: str | None = None):
    
    """
    Retourne les offres stockées avec filtres :
    - min_score
    - decision calculée automatiquement
    """

    try:
        if not os.path.exists(settings.JOB_OFFERS_PATH):
            return {
                "status": "empty",
                "message": "Aucune offre disponible"
            }

        with open(settings.JOB_OFFERS_PATH, "r", encoding="utf-8") as f:
            jobs = json.load(f)

        filtered_jobs = []

        for job in jobs:
            analysis = job.get("analysis", {})
            score = analysis.get("matching_score", 0)

            # Décision automatique
            if score >= 80:
                computed_decision = "APPLY"
            elif score >= 65:
                computed_decision = "REVIEW"
            else:
                computed_decision = "SKIP"

            # On ajoute la décision dans l'objet retourné
            job["decision"] = computed_decision

            if score >= min_score:
                if decision:
                    if computed_decision == decision:
                        filtered_jobs.append(job)
                else:
                    filtered_jobs.append(job)

        return {
            "status": "success",
            "total": len(jobs),
            "filtered": len(filtered_jobs),
            "data": filtered_jobs
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
        
# ---------------------------------------------------------
# 🏆 ROUTE : TOP OFFRES TRIÉES PAR SCORE
# ---------------------------------------------------------
@router.get("/top")
def get_top_jobs(limit: int = 10):
    """
    Retourne les meilleures offres triées par matching_score.

    Paramètre :
    - limit : nombre maximum d'offres retournées
    """

    try:
        if not os.path.exists(settings.JOB_OFFERS_PATH):
            return {
                "status": "empty",
                "message": "Aucune offre disponible"
            }

        # Charger les offres stockées
        with open(settings.JOB_OFFERS_PATH, "r", encoding="utf-8") as f:
            jobs = json.load(f)

        # Trier les offres par score décroissant
        sorted_jobs = sorted(
            jobs,
            key=lambda job: job.get("analysis", {}).get("matching_score", 0),
            reverse=True
        )

        # Limiter le nombre de résultats
        top_jobs = sorted_jobs[:limit]

        return {
            "status": "success",
            "total": len(jobs),
            "returned": len(top_jobs),
            "data": top_jobs
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }