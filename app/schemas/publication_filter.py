from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.publication import PublicationStatus, PublicationType


class PublicationFilter(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=10, ge=1, le=100)

    search: str | None = None

    status: PublicationStatus | None = None
    publication_type: PublicationType | None = None

    institution_id: UUID | None = None

    sort_by: Literal[
        "created_at",
        "title",
        "status",
        "publication_type",
    ] = "created_at"

    order: Literal["asc", "desc"] = "desc"
