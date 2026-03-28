"""
=====================================================================
📦 JOB OFFER MODEL - MODÈLE PYDANTIC POUR LES OFFRES D'EMPLOI
=====================================================================

🎯 RÔLE :
Ce fichier définit la structure d'une offre d'emploi pour la validation
des données API avec Pydantic.

📚 POUR UN DÉBUTANT :
Pydantic est comme un "filtre" qui s'assure que les données reçues
ont le bon format avant de les utiliser.

=====================================================================
"""

from pydantic import BaseModel, Field
from typing import Optional
import logging

# Configuration du logging
logger = logging.getLogger(__name__)


# ==============================================================
# 🔹 MODÈLE JOB OFFER (offre d'emploi)
# ==============================================================

class JobOffer(BaseModel):
    """
    Modèle représentant une offre d'emploi.

    📚 EXPLICATION :
    Ce modèle définit les champs obligatoires pour une offre d'emploi.
    """

    title: str = Field(..., description="Titre du poste")
    description: str = Field(..., description="Description de l'offre")
    location: str = Field(..., description="Localisation du poste")

    # Champs optionnels (pour plus d'informations)
    company: Optional[str] = Field(None, description="Nom de l'entreprise")
    url: Optional[str] = Field(None, description="URL de l'offre")
    id: Optional[str] = Field(None, description="ID de l'offre")

    class Config:
        """Configuration du modèle"""
        from_attributes = True
        json_schema_extra = {
            "example": {
                "title": "Data Scientist",
                "description": "Nous recherchons un Data Scientist passionné...",
                "location": "Paris",
                "company": "TechCorp",
                "url": "https://www.adzuna.fr/..."
            }
        }


# ==============================================================
# 🔹 SUPPRESSION DES PRINT (ils causaient l'erreur)
# ==============================================================

# ❌ Ces lignes ont été supprimées car elles n'ont pas leur place ici
# print(">>> ADZUNA_APP_ID =", ADZUNA_APP_ID)
# print(">>> ADZUNA_APP_KEY =", ADZUNA_APP_KEY)

# ✅ Si vous avez besoin d'afficher des informations de configuration,
#    faites-le dans le fichier config.py ou au démarrage de l'application,
#    pas dans un modèle.