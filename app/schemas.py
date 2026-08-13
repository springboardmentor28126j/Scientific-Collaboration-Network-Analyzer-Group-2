import re

from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Optional, List
from datetime import date

# ---------------- USERS ----------------
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    confirm_password: str
    role: str

    @model_validator(mode="after")
    def validate_password(self):
        if self.password != self.confirm_password:
            raise ValueError("Password and confirm password must match")
        if len(self.password) < 8:
            raise ValueError("Password must contain at least 8 characters")
        if not re.search(r"[A-Z]", self.password):
            raise ValueError("Password must include at least one uppercase letter")
        if not re.search(r"[a-z]", self.password):
            raise ValueError("Password must include at least one lowercase letter")
        if not re.search(r"\d", self.password):
            raise ValueError("Password must include at least one number")
        if not re.search(r"[^A-Za-z0-9]", self.password):
            raise ValueError("Password must include at least one special character")
        return self

class UserLogin(BaseModel):
    email: str
    password: str


class UserApproval(BaseModel):
    approved_role: str
    researcher_id: Optional[int] = None
    institution_id: Optional[int] = None


class UserRejection(BaseModel):
    reason: str = Field(min_length=3, max_length=500)


class UserAssignment(BaseModel):
    researcher_id: Optional[int] = None
    institution_id: Optional[int] = None


class UserStatusChange(BaseModel):
    account_status: str


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

    model_config = ConfigDict(from_attributes=True)

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

    model_config = ConfigDict(from_attributes=True)

class PublicationWithAuthors(BaseModel):
    id: int
    title: str
    authors: List[AuthorResponse]

    model_config = ConfigDict(from_attributes=True)

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

    model_config = ConfigDict(from_attributes=True)

class ConferenceParticipationCreate(BaseModel):
    researcher_id: int
    conference_id: int
    presentation_title: Optional[str] = None

class ConferenceParticipationResponse(BaseModel):
    id: int
    researcher_id: int
    conference_id: int
    presentation_title: Optional[str]

    model_config = ConfigDict(from_attributes=True)


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

    model_config = ConfigDict(from_attributes=True)


class CitationCreate(BaseModel):
    citing_publication_id: int
    cited_publication_id: int


class CitationResponse(BaseModel):
    id: int
    citing_publication_id: int
    cited_publication_id: int

    model_config = ConfigDict(from_attributes=True)


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


class ReviewAssignmentCreate(BaseModel):
    publication_id: int
    reviewer_id: int
    due_date: Optional[date] = None


class ReviewDecision(BaseModel):
    decision: str
    comments: str = Field(min_length=3, max_length=2000)
