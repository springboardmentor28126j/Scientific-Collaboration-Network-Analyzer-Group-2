from pydantic import BaseModel, EmailStr
from datetime import date

class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str
    institution_name: str | None = None


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
    location: str
    website: str | None = None
    phone: str | None = None


class InstitutionResponse(BaseModel):
    id: int
    user_id: int
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