from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel
from app.services.ai_agent import (
    analyze_offer,
    analyze_cv,
    match_cv_offer,
    optimize_cv_for_offer,
    cv_to_json,
    score_analysis,
    auto_apply
)

router = APIRouter()


# ---------------------------------------------------------
# MODELES Pydantic
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# ENDPOINTS
# ---------------------------------------------------------

@router.post("/analyze")
def analyze_job_offer(offer: Offer):
    return analyze_offer(offer)


@router.post("/match")
def match_endpoint(data: MatchRequest):
    return match_cv_offer(data.cv, data.offer)


@router.post("/optimize_cv")
def optimize_cv_endpoint(data: OptimizeRequest):
    return optimize_cv_for_offer(data.cv, data.offer, data.match)


@router.post("/cv_to_json")
async def cv_to_json_endpoint(file: UploadFile = File(...)):
    pdf_bytes = await file.read()
    return cv_to_json(pdf_bytes)


@router.post("/score")
def score_endpoint(data: ScoreRequest):
    return score_analysis(data.cv, data.offer)


@router.post("/auto_apply")
def auto_apply_endpoint(data: AutoApplyRequest):
    return auto_apply(data.cv_text, data.offer)


@router.post("/analyze_cv")
def analyze_cv_endpoint(cv: CV):
    from app.services.ai_agent import clean_cv_text
    cleaned = clean_cv_text(cv.text)
    return analyze_cv(cleaned)


from typing import List
from app.models.job import AnalyzedJob

@router.get("/job_suggestions", response_model=List[AnalyzedJob])
def job_suggestions():
    try:
        with open("job_offers.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return []


from fastapi import APIRouter
from app.services.job_search import fetch_and_store_job_offers

router = APIRouter()

@router.get("/refresh_jobs")
def refresh_jobs():
    fetch_and_store_job_offers()
    return {"status": "OK", "message": "Offres mises à jour"}
