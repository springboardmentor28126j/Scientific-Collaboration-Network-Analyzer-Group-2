from pydantic import BaseModel


class CitationCreate(BaseModel):
    citing_publication_id: int
    cited_publication_id: int


class CitationOut(CitationCreate):
    id: int

    class Config:
        from_attributes = True