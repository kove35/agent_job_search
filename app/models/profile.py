from pydantic import BaseModel

class UserProfile(BaseModel):
    name: str
    headline: str
    location: str
