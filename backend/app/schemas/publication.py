import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator, model_validator

from app.models.publication import PublicationStatus, PublicationType


class PublicationAuthorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    researcher_id: int
    email: str | None = None

    @model_validator(mode="before")
    @classmethod
    def _flatten(cls, obj):
        if hasattr(obj, "researcher_id"):
            email = None
            researcher = getattr(obj, "researcher", None)
            if researcher is not None and getattr(researcher, "user", None):
                email = researcher.user.email
            return {"researcher_id": obj.researcher_id, "email": email}
        return obj


class PublicationBase(BaseModel):
    title: str
    year: int | None = None
    venue: str | None = None
    doi_link: str | None = Field(default=None, max_length=500)
    abstract: str | None = None
    type: PublicationType | None = None
    status: PublicationStatus = PublicationStatus.DRAFT

    @field_validator("doi_link")
    @classmethod
    def validate_doi_format(cls, v: str | None) -> str | None:
        if v is None or not v.strip():
            return None
        v = v.strip()
        doi_pattern = re.compile(r"^(https?://(dx\.)?doi\.org/)?10\.\d{4,9}/\S+$", re.IGNORECASE)
        if not doi_pattern.match(v):
            raise ValueError("DOI must look like '10.xxxx/xxxxx' or a full https://doi.org/10.xxxx/xxxxx link")
        return v


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