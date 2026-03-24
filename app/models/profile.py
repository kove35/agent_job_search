from pydantic import BaseModel, Field
from typing import List, Optional


class UserProfile(BaseModel):
    skills: List[str] = Field(default_factory=list)
    job_targets: List[str] = Field(default_factory=list)
    experience_level: Optional[str] = None
    remote_only: bool = False
    locations: List[str] = Field(default_factory=list)
    salary_min: Optional[int] = None
    avoid_keywords: List[str] = Field(default_factory=list)