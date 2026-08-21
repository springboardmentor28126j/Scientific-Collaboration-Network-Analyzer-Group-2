from typing import Optional
from pydantic import BaseModel

# =====================================================
# Researcher Schemas
# =====================================================

class ResearcherCreate(BaseModel):
    full_name: str
    email: str
    institution: str
    department: str
    country: str


class ResearcherResponse(BaseModel):
    researcher_id: int
    full_name: str
    email: str
    institution: str
    department: str
    country: str

    class Config:
        from_attributes = True


# =====================================================
# Publication Schemas
# =====================================================

class PublicationCreate(BaseModel):
    title: str
    abstract: Optional[str] = None
    keywords: Optional[str] = None
    author: str
    journal: str
    year: int
    status: str = "Draft"
    pdf_file: Optional[str] = None
    researcher_id: int


class PublicationUpdate(BaseModel):
    title: Optional[str] = None
    abstract: Optional[str] = None
    keywords: Optional[str] = None
    author: Optional[str] = None
    journal: Optional[str] = None
    year: Optional[int] = None
    status: Optional[str] = None
    pdf_file: Optional[str] = None
    researcher_id: Optional[int] = None


class PublicationResponse(BaseModel):
    publication_id: int
    title: str
    abstract: Optional[str] = None
    keywords: Optional[str] = None
    author: str
    journal: str
    year: int
    status: str
    pdf_file: Optional[str] = None
    researcher_id: Optional[int] = None

    class Config:
        from_attributes = True
# =====================================================
# Collaboration Schemas
# =====================================================

class CollaborationCreate(BaseModel):
    researcher1_id: int
    researcher2_id: int
    project: str
    institution: Optional[str] = None
    collaboration_type: Optional[str] = None
    start_date: Optional[str] = None
    status: str = "Active"


class CollaborationResponse(BaseModel):
    collaboration_id: int
    researcher1_id: int
    researcher2_id: int
    project: str
    institution: Optional[str] = None
    collaboration_type: Optional[str] = None
    start_date: Optional[str] = None
    status: str

    class Config:
        from_attributes = True