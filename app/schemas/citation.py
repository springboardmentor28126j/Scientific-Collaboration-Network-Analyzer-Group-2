from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CitationBase(BaseModel):
    title: str
    authors: str
    journal: str | None = None
    year: int
    volume: str | None = None
    issue: str | None = None
    pages: str | None = None
    doi: str | None = None
    url: str | None = None
    citation_style: str
    formatted_citation: str | None = None


class CitationCreate(CitationBase):
    publication_id: UUID


class CitationUpdate(BaseModel):
    title: str | None = None
    authors: str | None = None
    journal: str | None = None
    year: int | None = None
    volume: str | None = None
    issue: str | None = None
    pages: str | None = None
    doi: str |None = None
    url: str | None = None
    citation_style: str | None = None
    formatted_citation: str | None = None


class CitationResponse(CitationBase):
    id: UUID
    publication_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
