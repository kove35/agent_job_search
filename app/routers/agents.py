"""
=====================================================================
📦 AGENT ROUTER (FASTAPI) - VERSION PROPRE (JSON ONLY)
=====================================================================
"""

import logging
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse

from pydantic import BaseModel
from app.models.job_offer import JobOffer

# ==============================================================
# 🔹 MODÈLE APPLY (VERSION PROPRE JSON)
# ==============================================================
class ApplyRequest(BaseModel):
    job: JobOffer
    cv_name: Optional[str] = None
    match_threshold: int = 50
    user_id: Optional[int] = None


# ==============================================================
# 🔹 SERVICES
# ==============================================================
from app.agents.autonomous_agent import run_autonomous_agent
from app.services.application_builder import build_application_pack
from app.services.storage import (
    get_cv_path,
    save_cv,
    list_cvs,
    delete_cv,
    get_cv_info,
    get_last_cv,
    get_default_cv,
    update_last_cv
)

# ==============================================================
# 🔹 LOGGING
# ==============================================================
logger = logging.getLogger(__name__)

# ==============================================================
# 🔹 ROUTER
# ==============================================================
router = APIRouter()

# ==============================================================
# 🔹 ENDPOINT 1 : RUN AGENT (inchangé)
# ==============================================================

@router.post("/run")
async def run_agent(
    file: Optional[UploadFile] = File(None),
    cv_name: Optional[str] = Form(None),
    max_jobs: int = Form(10),
    location: str = Form(""),
    match_threshold: int = Form(50),
    user_id: Optional[int] = Form(None)
):

    try:
        cv_path = None
        cv_filename = None

        if file:
            if not file.filename.endswith('.pdf'):
                raise HTTPException(status_code=400, detail="PDF uniquement")

            content = await file.read()

            cv_filename = save_cv(file.filename, content, set_as_last=True)
            cv_path = get_cv_path(cv_filename)

        elif cv_name:
            cv_path = get_cv_path(cv_name)
            cv_filename = cv_name
            update_last_cv(cv_filename)

        else:
            default_cv = get_default_cv()
            if not default_cv:
                raise HTTPException(status_code=404, detail="Aucun CV")

            cv_path = get_cv_path(default_cv)
            cv_filename = default_cv

        results = run_autonomous_agent(
            cv_pdf_path=cv_path,
            user_id=user_id,
            max_jobs=max_jobs,
            location=location,
            threshold=match_threshold,
            save_to_db=True
        )

        return {
            "success": True,
            "cv_used": cv_filename,
            "jobs": results,
            "nb_jobs": len(results)
        }

    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================
# 🔥 ENDPOINT 2 : APPLY (CORRIGÉ 100%)
# ==============================================================

@router.post("/apply")
async def apply_to_job(request: ApplyRequest):

    logger.info(f"apply_to_job - Offre: {request.job.title}")

    try:
        # ==========================================================
        # 📄 1️⃣ RÉCUPÉRATION DONNÉES
        # ==========================================================
        job = request.job
        cv_name = request.cv_name
        match_threshold = request.match_threshold
        user_id = request.user_id

        # ==========================================================
        # 📄 2️⃣ RÉCUPÉRATION CV
        # ==========================================================
        if cv_name:
            cv_path = get_cv_path(cv_name)
            cv_filename = cv_name
            update_last_cv(cv_filename)
        else:
            default_cv = get_default_cv()
            if not default_cv:
                raise HTTPException(status_code=404, detail="Aucun CV")

            cv_path = get_cv_path(default_cv)
            cv_filename = default_cv

        # ==========================================================
        # 📝 3️⃣ DESCRIPTION FALLBACK
        # ==========================================================
        if not job.description or job.description.strip() == "":
            job.description = f"""
Offre d'emploi pour le poste de {job.title} chez {job.company}.
Localisation : {job.location}
"""

        # ==========================================================
        # 🤖 4️⃣ GÉNÉRATION
        # ==========================================================
        pack = build_application_pack(
            job=job,
            cv_pdf_path=cv_path,
            user_id=user_id,
            save_to_db=True,
            generate_pdf=False
        )

        if not pack:
            raise HTTPException(status_code=500, detail="Erreur génération")

        return {
            "success": True,
            "cv_used": cv_filename,
            "match_score": pack.match_score,
            "cover_letter": pack.cover_letter,
            "missing_skills": pack.missing_skills,
            "strengths": pack.strengths
        }

    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================
# 🔹 CV LIST
# ==============================================================

@router.get("/cv/list")
async def list_cv():
    try:
        cvs = list_cvs()
        last_cv = get_last_cv()

        return {
            "success": True,
            "cvs": [get_cv_info(cv) for cv in cvs],
            "count": len(cvs),
            "last_cv": last_cv
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================
# 🔹 UPLOAD CV
# ==============================================================

@router.post("/cv/upload")
async def upload_cv(file: UploadFile = File(...), set_as_last: bool = Form(True)):

    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="PDF uniquement")

        content = await file.read()

        filename = save_cv(file.filename, content, set_as_last=set_as_last)

        return {
            "success": True,
            "filename": filename
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================
# 🔹 DELETE CV
# ==============================================================

@router.delete("/cv/{filename}")
async def delete_cv_endpoint(filename: str):
    delete_cv(filename)
    return {"success": True}


# ==============================================================
# 🔹 GET CV FILE
# ==============================================================

@router.get("/cv/file/{filename}")
async def get_cv_file(filename: str):
    try:
        file_path = get_cv_path(filename)
        return FileResponse(file_path, media_type="application/pdf")
    except:
        raise HTTPException(status_code=404, detail="Not found")


# ==============================================================
# 🔹 HISTORY
# ==============================================================

@router.get("/applications")
async def get_applications_history(limit: int = 100):
    from app.services.storage import get_applications
    apps = get_applications(limit=limit)
    return {"success": True, "applications": apps}