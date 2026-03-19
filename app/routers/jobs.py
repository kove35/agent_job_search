from fastapi import APIRouter
from app.services.job_search import fetch_and_store_job_offers

router = APIRouter()

@router.get("/refresh_jobs")
def refresh_jobs():
    fetch_and_store_job_offers()
    return {"status": "OK", "message": "Offres mises à jour"}
