"""
=====================================================================
📦 CV OPTIMIZATION ROUTER - API POUR L'OPTIMISATION DU CV
=====================================================================
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os

from app.services.cv_optimizer import optimize_cv_for_job
from app.services.pdf_generator import generate_cv_pdf
from app.services.storage.cv_storage import get_cv_path, get_cv_text

router = APIRouter(prefix="/cv", tags=["cv-optimization"])


class OptimizeCVRequest(BaseModel):
    """Modèle pour la requête d'optimisation de CV"""
    cv_name: str
    job_title: str
    job_description: str
    missing_skills: List[str] = []
    strengths: List[str] = []


class OptimizeCVResponse(BaseModel):
    """Modèle pour la réponse d'optimisation de CV"""
    optimized_text: str
    pdf_path: Optional[str] = None
    success: bool
    error: Optional[str] = None


@router.post("/optimize", response_model=OptimizeCVResponse)
async def optimize_cv(request: OptimizeCVRequest):
    """
    Optimise un CV pour une offre d'emploi spécifique.
    
    Args:
        request: Requête avec le nom du CV et les infos de l'offre
    
    Returns:
        CV optimisé (texte et PDF)
    """
    try:
        # Récupérer le CV
        cv_path = get_cv_path(request.cv_name)
        cv_text = get_cv_text(cv_path)
        
        if not cv_text:
            return OptimizeCVResponse(
                optimized_text="",
                pdf_path=None,
                success=False,
                error="Impossible de lire le CV"
            )
        
        # Optimiser le CV
        optimized_text = optimize_cv_for_job(
            cv_text=cv_text,
            job_title=request.job_title,
            job_description=request.job_description,
            missing_skills=request.missing_skills,
            strengths=request.strengths
        )
        
        # Générer le PDF
        from app.core.user_config import USER_CONFIG
        user_name = USER_CONFIG.get("name", "Candidat")
        
        pdf_path = generate_cv_pdf(
            cv_text=optimized_text,
            job_title=request.job_title,
            user_name=user_name
        )
        
        return OptimizeCVResponse(
            optimized_text=optimized_text,
            pdf_path=pdf_path,
            success=True,
            error=None
        )
        
    except Exception as e:
        return OptimizeCVResponse(
            optimized_text="",
            pdf_path=None,
            success=False,
            error=str(e)
        )