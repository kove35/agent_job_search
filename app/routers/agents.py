# =========================================================
# 📦 AGENT ROUTER (FASTAPI) — VERSION PRO
# =========================================================

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse

# 🔥 CORE
from app.agents.autonomous_agent import run_autonomous_agent

# 📄 CV
from app.services.storage import get_cv_path, save_cv, list_cvs, delete_cv

# 📦 APPLY
from app.services.application_builder import build_application_pack

router = APIRouter()


# =========================================================
# 🔍 RUN AGENT
# =========================================================
@router.post("/agent/run")
async def run_agent(
    file: UploadFile = File(None),
    cv_name: str = Form(None),
    max_jobs: int = Form(10),
    location: str = Form("")
):
    """
    🎯 Lance l’agent IA

    🧠 ALGO BACKEND :
    -----------------
    1. récupérer CV :
        - upload → sauvegarde temporaire
        - ou CV existant
    2. obtenir chemin fichier
    3. appeler agent IA
    4. retourner résultats
    """

    try:
        # =====================================================
        # 📄 1️⃣ RÉCUPÉRATION CV
        # =====================================================
        if file:
            content = await file.read()

            # 🔥 sauvegarde temporaire
            filename = save_cv(file.filename, content)
            cv_path = get_cv_path(filename)

        elif cv_name:
            cv_path = get_cv_path(cv_name)

        else:
            return JSONResponse(
                status_code=400,
                content={"error": "Aucun CV fourni"}
            )

        # =====================================================
        # 🤖 2️⃣ AGENT
        # =====================================================
        results = run_autonomous_agent(
            cv_pdf_path=cv_path,
            profile=cv_path,  # temporaire (tu peux améliorer)
            max_jobs=max_jobs,
            location=location  # ✅ Ajout du paramètre location
        )

        # =====================================================
        # 📦 3️⃣ RETURN
        # =====================================================
        return {
            "jobs": results,
            "nb_jobs": len(results)
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


# =========================================================
# 📩 APPLY
# =========================================================
@router.post("/agent/apply")
async def apply_to_job(
    job: dict,
    cv_name: str = Form(None)
):
    """
    🎯 Génère CV + lettre pour UNE offre

    🧠 ALGO :
    ----------
    1. récupérer CV
    2. lancer pipeline IA
    3. retourner PDF + texte
    """

    try:
        if not cv_name:
            return JSONResponse(
                status_code=400,
                content={"error": "CV manquant"}
            )

        # chemin CV
        cv_path = get_cv_path(cv_name)

        # =====================================================
        # 🤖 BUILD PACK
        # =====================================================
        pack = build_application_pack(job, cv_path)

        if not pack:
            return JSONResponse(
                status_code=500,
                content={"error": "Erreur génération"}
            )

        return {
            "cover_letter": pack.cover_letter,
            "cv_pdf": pack.cv_version_path,
            "letter_pdf": getattr(pack, "letter_pdf", None),
            "score": pack.match_score
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


# =========================================================
# 📂 CV LIST
# =========================================================
@router.get("/cv/list")
def list_cv():
    """
    🎯 Liste des CV stockés
    """
    return {"cvs": list_cvs()}


# =========================================================
# 📤 CV UPLOAD
# =========================================================
@router.post("/cv/upload")
async def upload_cv(file: UploadFile = File(...)):
    """
    🎯 Upload CV
    """

    content = await file.read()

    filename = save_cv(file.filename, content)

    return {"filename": filename, "success": True}


# =========================================================
# ❌ CV DELETE
# =========================================================
@router.post("/cv/delete")
def delete_cv_endpoint(filename: str = Form(...)):
    """
    🎯 Suppression CV
    """

    delete_cv(filename)

    return {"deleted": True, "filename": filename}


# =========================================================
# 📊 APPLICATIONS HISTORY
# =========================================================
@router.get("/applications")
def get_applications():
    """
    🎯 Récupère l'historique des candidatures
    """
    try:
        from app.services.history import get_applications_history
        return {"applications": get_applications_history()}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "applications": []}
        )