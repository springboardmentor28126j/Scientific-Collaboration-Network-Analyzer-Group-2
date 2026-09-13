from typing import Optional
from pydantic import BaseModel
from datetime import date


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

    # NEW: Publication Type
    publication_type: str = "Journal Paper"

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

    # NEW: Publication Type
    publication_type: Optional[str] = None

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

    # NEW: Publication Type
    publication_type: str

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
    start_date: Optional[date] = None
    status: str

    class Config:
        from_attributes = True


# =====================================================
# Conference Schemas
# =====================================================

class ConferenceCreate(BaseModel):
    conference_name: str
    location: str
    conference_date: str
    publication_id: int


class ConferenceResponse(BaseModel):
    conference_id: int
    conference_name: str
    location: str
    conference_date: str
    publication_id: int

    class Config:
        from_attributes = True
    # =====================================================
# Review Schemas
# =====================================================

class ReviewCreate(BaseModel):
    publication_id: int
    reviewer_id: int
    review_feedback: Optional[str] = None
    decision: str = "Pending"
    status: str = "Pending"


class ReviewResponse(BaseModel):
    review_id: int
    publication_id: int
    reviewer_id: int
    review_feedback: Optional[str] = None
    decision: str
    status: str

    class Config:
        from_attributes = True