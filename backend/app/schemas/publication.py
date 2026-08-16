from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.publication import PublicationType, PublicationStatus


class PublicationCreate(BaseModel):
    title: str
    abstract: str | None = None
    publication_type: PublicationType
    venue_name: str | None = None
    doi: str | None = None
    publication_date: date | None = None
    file_path: str | None = None
    co_author_ids: list[int] = []


class PublicationUpdate(BaseModel):
    """
    For the primary author. Deliberately has NO status field -- a
    researcher submitting their own paper cannot set it to "published"
    themselves. Status changes go through the separate
    PublicationStatusUpdate / PATCH /publications/{id}/status endpoint,
    which is restricted to institution admins.
    """
    title: str | None = None
    abstract: str | None = None
    venue_name: str | None = None
    doi: str | None = None
    publication_date: date | None = None
    file_path: str | None = None
    co_author_ids: list[int] | None = None


class PublicationStatusUpdate(BaseModel):
    status: PublicationStatus


class PublicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    publication_id: int
    title: str
    abstract: str | None
    publication_type: PublicationType
    status: PublicationStatus
    primary_author_id: int
    institution_id: int | None
    venue_name: str | None
    doi: str | None
    publication_date: date | None
    file_path: str | None
    created_at: datetime
    updated_at: datetime
    co_author_ids: list[int] = []

class PublicationListResponse(BaseModel):
    items: list[PublicationOut]
    total: int
    page: int
    page_size: int
    