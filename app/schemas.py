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