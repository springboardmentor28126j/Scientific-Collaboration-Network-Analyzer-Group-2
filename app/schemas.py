from pydantic import BaseModel

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