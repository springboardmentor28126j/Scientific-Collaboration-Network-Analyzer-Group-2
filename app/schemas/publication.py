from datetime import datetime
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, ConfigDict, HttpUrl


class PublicationType(str, Enum):
    JOURNAL = "Journal"
    CONFERENCE = "Conference"
    BOOK = "Book"
    BOOK_CHAPTER = "BookChapter"
    PATENT = "Patent"
    THESIS = "Thesis"


class PublicationStatus(str, Enum):
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    ACCEPTED = "Accepted"
    PUBLISHED = "Published"
    REJECTED = "Rejected"


class PublicationBase(BaseModel):
    title: str
    abstract: str | None = None
    doi: str | None = None
    journal: str | None = None
    conference: str | None = None
    publication_year: int
    publication_type: PublicationType
    status: PublicationStatus = PublicationStatus.DRAFT
    url: HttpUrl | None = None
    citation_count: int = 0


class PublicationCreate(PublicationBase):
    pass


class PublicationUpdate(BaseModel):
    title: str | None = None
    abstract: str | None = None
    doi: str | None = None
    journal: str | None = None
    conference: str | None = None
    publication_year: int | None = None
    publication_type: PublicationType | None = None
    status: PublicationStatus | None = None
    url: HttpUrl | None = None
    citation_count: int | None = None


class PublicationResponse(PublicationBase):
    id: UUID

    owner_id: UUID

    file_name: str | None = None
    file_path: str | None = None
    file_size: int | None = None
    file_type: str | None = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
