from pydantic import BaseModel
from datetime import datetime


class CitationBase(BaseModel):

    paper_id: int
    cited_paper_id: int
    citation_year: int
    citation_count: int = 1


class CitationCreate(CitationBase):
    pass


class CitationResponse(CitationBase):

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True