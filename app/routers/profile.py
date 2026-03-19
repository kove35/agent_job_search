from fastapi import APIRouter
from app.models.profile import UserProfile

router = APIRouter(prefix="/profile", tags=["Profil"])

@router.post("/")
def create_or_update_profile(profile: UserProfile):
    """
    Reçoit un profil utilisateur et le renvoie.
    Plus tard : on le stockera en base de données.
    """
    return {
        "message": "Profil reçu",
        "data": profile
    }
