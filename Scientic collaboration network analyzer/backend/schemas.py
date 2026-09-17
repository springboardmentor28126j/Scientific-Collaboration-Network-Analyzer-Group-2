from pydantic import BaseModel


# Schema for creating a new researcher
class ResearcherCreate(BaseModel):
    full_name: str
    email: str
    institution: str
    department: str
    country: str


# Schema for displaying researcher information
class ResearcherResponse(BaseModel):
    researcher_id: int
    full_name: str
    email: str
    institution: str
    department: str
    country: str

    class Config:
        from_attributes = True