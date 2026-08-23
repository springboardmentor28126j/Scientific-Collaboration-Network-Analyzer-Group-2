from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, computed_field

from app.models.publication import PublicationStatus, PublicationType


class PublicationAuthorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    researcher_id: int
    email: str | None = None


class PublicationBase(BaseModel):
    title: str
    year: int | None = None
    venue: str | None = None
    doi_link: str | None = None
    abstract: str | None = None
    type: PublicationType | None = None
    status: PublicationStatus = PublicationStatus.DRAFT


class PublicationCreate(PublicationBase):
    # Co-author researcher ids in addition to the researcher creating the entry,
    # who is always added as an author automatically.
    coauthor_ids: list[int] = []


class PublicationUpdate(PublicationBase):
    coauthor_ids: list[int] = []


class PublicationOut(PublicationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    authors: list[PublicationAuthorOut] = []
    stored_filename: str | None = None
    original_filename: str | None = None
    reviewed_by: int | None = None
    review_comment: str | None = None
    reviewed_at: datetime | None = None

    @computed_field
    @property
    def file_url(self) -> str | None:
        if self.stored_filename:
            return f"/uploads/publication_files/{self.stored_filename}"
        return None


class PublicationReviewDecision(BaseModel):
    decision: Literal["approve", "reject"]
    comment: str | None = None
