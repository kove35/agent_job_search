from fastapi import APIRouter
from app.agents.application_agent import build_application
from app.services.storage.application_storage import get_applications

router = APIRouter()


@router.post("/applications/build")
def create_application(data: dict):
    job = data.get("job")
    cv_text = data.get("cv_text")
    return build_application(job, cv_text)


# 🔥 NOUVELLE ROUTE
@router.get("/applications")
def read_applications():
    return get_applications()