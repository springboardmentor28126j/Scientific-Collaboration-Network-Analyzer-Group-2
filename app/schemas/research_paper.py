from pydantic import BaseModel


# -----------------------------
# Base Schema
# -----------------------------
class ResearchPaperBase(BaseModel):

    title: str

    authors: str

    abstract: str | None = None

    publication_year: int

    source: str

    doi: str

    keywords: str | None = None

    status: str = "Draft"

    paper_file: str | None = None


# -----------------------------
# Create Schema
# -----------------------------
class ResearchPaperCreate(ResearchPaperBase):
    pass


# -----------------------------
# Update Schema
# -----------------------------
class ResearchPaperUpdate(BaseModel):

    title: str

    authors: str

    abstract: str | None = None

    publication_year: int

    source: str

    doi: str

    keywords: str | None = None

    status: str

    paper_file: str | None = None


# -----------------------------
# Response Schema
# -----------------------------
class ResearchPaperResponse(ResearchPaperBase):

    id: int

    researcher_id: int | None = None

    class Config:
        from_attributes = True