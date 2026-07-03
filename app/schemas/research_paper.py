from pydantic import BaseModel


class ResearchPaperBase(BaseModel):
    title: str
    authors: str
    abstract: str
    publication_year: int
    source: str
    doi: str


class ResearchPaperCreate(ResearchPaperBase):
    pass


class ResearchPaperResponse(ResearchPaperBase):
    id: int

    class Config:
        from_attributes = True