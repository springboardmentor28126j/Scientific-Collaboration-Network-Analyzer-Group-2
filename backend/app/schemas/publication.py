from pydantic import BaseModel
from typing import Optional
from app.models.publication import PublicationType, PublicationStatus

class PublicationCreate(BaseModel):
    title: str
    type: PublicationType
    doi: Optional[str] = None
    author_id: int

class PublicationUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[PublicationStatus] = None
    doi: Optional[str] = None

class PublicationOut(BaseModel):
    id: int
    title: str
    type: PublicationType
    status: PublicationStatus
    doi: Optional[str]
    author_id: int

    class Config:
        from_attributes = True
