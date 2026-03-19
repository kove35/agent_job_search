from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from app.db.database import Base


class Application(Base):
    """
    Table des candidatures
    """

    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)

    job_id = Column(String)
    title = Column(String)
    company = Column(String)

    decision = Column(String)
    score = Column(Float)

    cover_letter = Column(String)
    tailored_cv = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)