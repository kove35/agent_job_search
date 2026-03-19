from pydantic import BaseModel
from typing import Optional

class JobOffer(BaseModel):
    title: str
    company: Optional[str]
    location: Optional[str]
    description: Optional[str]
    url: Optional[str]

class AnalyzedJob(BaseModel):
    offer: JobOffer
    analysis: str
