from pydantic import BaseModel

class JobOffer(BaseModel):
    """
    Modèle représentant une offre d'emploi.
    """
    title: str
    description: str
    location: str


print(">>> ADZUNA_APP_ID =", ADZUNA_APP_ID)
print(">>> ADZUNA_APP_KEY =", ADZUNA_APP_KEY)
