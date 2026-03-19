from pydantic import BaseModel
from typing import Optional


class ApplicationPack(BaseModel):
    offer_id: str
    offer_title: str
    company: str
    location: Optional[str]
    match_score: float
    cv_version_path: Optional[str]  # chemin vers le CV personnalisé (PDF ou autre)
    cover_letter: str               # texte de la lettre de motivation
    url: Optional[str]
    created_at: str                 # ISO datetime string
    status: str                     # "pending", "sent", "ignored"
