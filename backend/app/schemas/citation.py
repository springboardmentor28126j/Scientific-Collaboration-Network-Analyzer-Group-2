from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CitationBase(BaseModel):
    citing_publication_id: int
    cited_publication_id: int
    title: Optional[str] = None
    authors: Optional[str] = None
    journal: Optional[str] = None
    year: Optional[int] = None
    doi: Optional[str] = None
    citation_style: str = "APA"
    formatted_citation: Optional[str] = None

class CitationCreate(CitationBase):
    pass

class CitationUpdate(BaseModel):
    title: Optional[str] = None
    authors: Optional[str] = None
    journal: Optional[str] = None
    year: Optional[int] = None
    doi: Optional[str] = None
    citation_style: Optional[str] = None
    formatted_citation: Optional[str] = None

class Citation(CitationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True