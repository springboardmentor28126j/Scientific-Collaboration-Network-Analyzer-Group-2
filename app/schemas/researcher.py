from pydantic import BaseModel


class ResearcherBase(BaseModel):
    full_name: str
    email: str
    institution: str
    department: str
    specialization: str
    h_index: int
    total_publications: int


class ResearcherCreate(ResearcherBase):
    pass


class ResearcherResponse(ResearcherBase):
    id: int

    class Config:
        from_attributes = True