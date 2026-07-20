from pydantic import BaseModel
from datetime import date

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str


class UserLogin(BaseModel):
    email: str
    password: str

class ResearcherCreate(BaseModel):
    full_name: str
    department: str
    institution: str
    skills: str
    research_interest: str
    designation: str
    institution_id: int | None = None

class InstitutionCreate(BaseModel):
    name: str
    address: str | None = None
    website: str | None = None
    contact_email: str | None = None

class PublicationCreate(BaseModel):
    title: str
    abstract: str | None = None
    publication_type: str
    status: str = "draft"
    doi: str | None = None
    publication_date: date | None = None
    journal_or_venue: str | None = None
    institution_id: int | None = None

class PublicationAuthorAssign(BaseModel):
    publication_id: int
    researcher_ids: list[int]

class AuthorResponse(BaseModel):
    id: int
    full_name: str

    class Config:
        orm_mode = True


class PublicationWithAuthors(BaseModel):
    id: int
    title: str
    authors: list[AuthorResponse]

    class Config:
        orm_mode = True