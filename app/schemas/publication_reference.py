from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PublicationReferenceCreate(BaseModel):
    title: str = Field(max_length=500)

    authors: str = Field(max_length=1000)

    publication_name: str | None = Field(
        default=None,
        max_length=255,
    )

    year: int | None = None

    doi: str | None = Field(
        default=None,
        max_length=255,
    )

    url: str | None = Field(
        default=None,
        max_length=1000,
    )


class PublicationReferenceUpdate(BaseModel):
    reference_order: int | None = Field(
        default=None,
        gt=0,
    )

    title: str | None = Field(
        default=None,
        max_length=500,
    )

    authors: str | None = Field(
        default=None,
        max_length=1000,
    )

    publication_name: str | None = Field(
        default=None,
        max_length=255,
    )

    year: int | None = None

    doi: str | None = Field(
        default=None,
        max_length=255,
    )

    url: str | None = Field(
        default=None,
        max_length=1000,
    )


class PublicationReferenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID

    reference_order: int

    title: str

    authors: str

    publication_name: str | None

    year: int | None

    doi: str | None

    url: str | None
