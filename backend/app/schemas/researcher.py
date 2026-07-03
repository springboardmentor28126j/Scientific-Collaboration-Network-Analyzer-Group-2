from pydantic import BaseModel
from typing import Optional

class ResearcherCreate(BaseModel):
    full_name: str
    department: Optional[str] = None
    institution: Optional[str] = None
    research_interests: Optional[str] = None
    skills: Optional[str] = None

class ResearcherOut(ResearcherCreate):
    id: int

    class Config:
        from_attributes = True
