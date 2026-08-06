from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

# ---------------- USERS ----------------
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str

class UserLogin(BaseModel):
    email: str
    password: str


class UserApproval(BaseModel):
    approved_role: str


class AnnouncementCreate(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    message: str = Field(min_length=3, max_length=1000)
    recipient_ids: Optional[List[str]] = None
    link: Optional[str] = None
    send_email: bool = True

# ---------------- INSTITUTIONS ----------------
class InstitutionCreate(BaseModel):
    name: str
    address: Optional[str] = None
    website: Optional[str] = None
    contact_email: Optional[str] = None

# ---------------- RESEARCHERS ----------------
class ResearcherCreate(BaseModel):
    full_name: str
    department: str
    skills: str
    research_interest: str
    designation: str
    institution_id: int   
    email: Optional[str] = None

class AuthorResponse(BaseModel):
    id: int
    full_name: str

    class Config:
        from_attributes = True

# ---------------- PUBLICATIONS ----------------
class PublicationCreate(BaseModel):
    title: str
    abstract: Optional[str] = None
    publication_type: str
    status: str = "draft"
    doi: Optional[str] = None
    publication_date: Optional[date] = None
    journal_or_venue: Optional[str] = None
    institution_id: Optional[int] = None
    researcher_ids: List[int] = Field(default_factory=list)

class PublicationResponse(BaseModel):
    id: int
    title: str
    abstract: Optional[str]
    publication_type: str
    status: str
    doi: Optional[str]

    class Config:
        from_attributes = True

class PublicationWithAuthors(BaseModel):
    id: int
    title: str
    authors: List[AuthorResponse]

    class Config:
        from_attributes = True

class PublicationAuthorAssign(BaseModel):
    publication_id: int
    researcher_ids: List[int]

# ---------------- CONFERENCES ----------------
class ConferenceCreate(BaseModel):
    name: str
    location: Optional[str] = None
    start_date: date
    end_date: date

class ConferenceResponse(BaseModel):
    id: int
    name: str
    location: Optional[str]
    start_date: date
    end_date: date

    class Config:
        from_attributes = True

class ConferenceParticipationCreate(BaseModel):
    researcher_id: int
    conference_id: int
    presentation_title: Optional[str] = None

class ConferenceParticipationResponse(BaseModel):
    id: int
    researcher_id: int
    conference_id: int
    presentation_title: Optional[str]

    class Config:
        from_attributes = True


class CollaborationCreate(BaseModel):
    researcher1_id: int
    researcher2_id: int
    project: Optional[str] = None
    publication_id: Optional[int] = None


class CollaborationResponse(BaseModel):
    id: int
    researcher1_id: int
    researcher2_id: int
    project: Optional[str] = None
    publication_id: Optional[int] = None
    status: str = "pending"

    class Config:
        from_attributes = True


class CitationCreate(BaseModel):
    citing_publication_id: int
    cited_publication_id: int


class CitationResponse(BaseModel):
    id: int
    citing_publication_id: int
    cited_publication_id: int

    class Config:
        from_attributes = True


class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    funding_agency: Optional[str] = None
    status: str = "planned"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    institution_id: Optional[int] = None


class ProjectAssignmentCreate(BaseModel):
    researcher_id: int
    role: str = "Member"
