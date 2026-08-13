import uuid
from datetime import datetime

from pydantic import Field

from app.models.publication import PublicationStatus, PublicationType
from app.schemas.common import ORMBase


class PublicationCreate(ORMBase):
    title: str = Field(min_length=5, max_length=500)
    abstract: str = Field(min_length=50)
    publication_type: PublicationType
    doi: str | None = Field(default=None, max_length=255)
    # pdf_url: str | None = Field(default=None, max_length=1000)


class PublicationUpdate(ORMBase):
    title: str | None = Field(default=None, min_length=5, max_length=500)
    abstract: str | None = Field(default=None, min_length=50)
    publication_type: PublicationType | None = None
    doi: str | None = Field(default=None, max_length=255)
    pdf_url: str | None = Field(default=None, max_length=1000)


class PublicationRead(ORMBase):
    id: uuid.UUID
    title: str
    abstract: str
    publication_type: PublicationType
    status: PublicationStatus
    doi: str | None
    pdf_url: str | None
    created_by: uuid.UUID
    submitted_at: datetime | None
    published_at: datetime | None
    archived_at: datetime | None
    created_at: datetime
    updated_at: datetime


class PublicationListItem(ORMBase):
    id: uuid.UUID
    title: str
    publication_type: PublicationType
    status: PublicationStatus
    created_at: datetime
