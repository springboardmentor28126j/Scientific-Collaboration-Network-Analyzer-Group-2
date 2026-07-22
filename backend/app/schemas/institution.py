from pydantic import BaseModel
from typing import Optional


class InstitutionCreate(BaseModel):
    name: str
    type: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None


class InstitutionOut(InstitutionCreate):
    id: int

    class Config:
        from_attributes = True