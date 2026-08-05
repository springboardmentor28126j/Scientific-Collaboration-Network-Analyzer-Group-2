from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional

class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str
    institution_id: int | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True

class ResearcherCreate(BaseModel):
    full_name: str
    email: EmailStr
    department: str
    institution: str
    designation: str
    research_interests: str | None = None
    skills: str | None = None
    phone: str | None = None

class ResearcherProfileCreate(BaseModel):

    institution: str
    department: str
    designation: str
    research_interests: str | None = None
    skills: str | None = None
    phone: str | None = None


class ResearcherUpdate(BaseModel):
    full_name: str
    email: EmailStr
    department: str
    institution: str
    designation: str
    research_interests: str | None = None
    skills: str | None = None
    phone: str | None = None



class ResearcherResponse(BaseModel):
    id: int
    user_id: int | None = None
    full_name: str
    email: EmailStr
    department: str
    institution: str
    designation: str
    research_interests: str | None = None
    skills: str | None = None
    phone: str | None = None

    
    class Config:
        from_attributes = True

class PublicationCreate(BaseModel):
    researcher_id: int
    title: str
    publication_type: str
    journal_name: str | None = None
    conference_name: str | None = None
    publication_year: int
    doi: str | None = None
    status: str
    publication_file: str | None = None


class PublicationUpdate(BaseModel):
    researcher_id: int
    title: str
    publication_type: str
    journal_name: str | None = None
    conference_name: str | None = None
    publication_year: int
    doi: str | None = None
    status: str
    publication_file: str | None = None


class PublicationResponse(BaseModel):
    id: int
    researcher_id: int

    researcher_name: str | None = None

    title: str
    publication_type: str

    journal_name: str | None = None
    conference_name: str | None = None

    publication_year: int

    doi: str | None = None
    status: str

    publication_file: str | None = None

    class Config:
        from_attributes = True
        
class InstitutionCreate(BaseModel):
    name: str
    institution_type: str | None = None
    location: str
    website: str | None = None
    phone: str | None = None

class InstitutionUpdate(BaseModel):
    institution_type: str | None = None
    location: str | None = None
    website: str | None = None
    phone: str | None = None

class InstitutionResponse(BaseModel):
    id: int
    user_id: int | None = None
    name: str
    institution_type: str | None = None
    location: str
    website: str | None = None
    phone: str | None = None

    class Config:
        from_attributes = True
        
# ---------------- Conference Schemas ----------------

class ConferenceCreate(BaseModel):

    title: str

    organizer: str

    location: str

    conference_date: str

    website: str | None = None

    institution: str

    event_type: str


class ConferenceUpdate(BaseModel):

    title: str | None = None

    location: str | None = None

    conference_date: str | None = None

    website: str | None = None



class ConferenceResponse(BaseModel):

    id: int

    title: str

    organizer: str

    location: str

    conference_date: str

    website: str | None = None

    institution: str

    event_type: str


    class Config:

        from_attributes = True

# ---------------- Conference Registration Schemas ----------------

class ConferenceRegistrationCreate(BaseModel):

    conference_id: int

    participation_type: str
    # Attendee / Presenter

    presentation_title: str | None = None

    publication_id: int | None = None

    presentation_mode: str | None = None
    # Oral / Poster



class ConferenceRegistrationResponse(BaseModel):

    id: int

    researcher_id: int

    researcher_name: str | None = None

    conference_id: int

    conference_title: str | None = None

    participation_type: str

    presentation_title: str | None = None

    publication_id: int | None = None

    presentation_mode: str | None = None

    status: str

    registration_date: date | None = None


    class Config:
        from_attributes = True

# ==========================
# Project Schemas
# ==========================

class ProjectBase(BaseModel):

    project_name: str

    description: Optional[str] = None

    start_date: date

    end_date: Optional[date] = None

    status: str = "Planned"

    institution_id: int



class ProjectCreate(ProjectBase):
    pass



class ProjectUpdate(BaseModel):

    project_name: Optional[str] = None

    description: Optional[str] = None

    start_date: Optional[date] = None

    end_date: Optional[date] = None

    status: Optional[str] = None

    institution_id: Optional[int] = None



class ProjectResponse(ProjectBase):

    id: int

    created_at: datetime

    institution_name: Optional[str] = None


    class Config:
        from_attributes = True

# ==========================
# Researcher Collaboration View Schema
# ==========================

class TeamMemberDetails(BaseModel):

    name: str

    role: str


class ResearcherCollaborationResponse(BaseModel):

    id: int

    project_name: str

    institution_name: str | None = None

    status: str

    start_date: date

    end_date: date | None = None

    description: str | None = None


    team_count: int

    collaboration_count: int


    team: list[TeamMemberDetails] = []

    collaborating_institutions: list[str] = []


    class Config:
        from_attributes = True

# ==========================
# Project Member Schemas
# ==========================

class ProjectMemberBase(BaseModel):

    project_id: int

    researcher_id: int

    role: str = "Team Member"


class ProjectMemberCreate(ProjectMemberBase):
    pass


class ProjectMemberResponse(ProjectMemberBase):

    id: int

    researcher_name: str

    assigned_at: datetime

    class Config:
        from_attributes = True

# ==========================
# Institution Collaboration Schemas
# ==========================

class InstitutionCollaborationCreate(BaseModel):

    project_id: int

    collaborating_institution_id: int



class InstitutionCollaborationResponse(BaseModel):

    id: int

    project_id: int

    project_name: str

    institution_id: int

    institution_name: str

    collaborating_institution_id: int

    collaborating_institution_name: str

    created_at: datetime


    class Config:
        from_attributes = True

class CitationCreate(BaseModel):

    publication_id: int

    cited_publication_id: int



class CitationResponse(BaseModel):

    id: int

    publication_id: int

    cited_publication_id: int

    created_at: datetime


    class Config:
        from_attributes = True

class ReferenceCreate(BaseModel):

    publication_id: int

    reference_title: str

    author: str | None = None

    publication_year: int | None = None

    doi: str | None = None



class ReferenceResponse(BaseModel):

    id: int

    publication_id: int

    reference_title: str

    author: str | None = None

    publication_year: int | None = None

    doi: str | None = None

    created_at: datetime


    class Config:
        from_attributes = True
        
class ActivityLogBase(BaseModel):

    action: str

    description: str


class ActivityLogCreate(ActivityLogBase):

    user_id: int


class ActivityLogResponse(ActivityLogBase):

    id: int

    user_id: int

    created_at: datetime

    class Config:
        from_attributes = True