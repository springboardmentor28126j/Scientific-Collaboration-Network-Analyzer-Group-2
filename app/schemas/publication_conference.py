from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.publication_conference import ConferenceOutcome


class PublicationConferenceCreate(BaseModel):
    conference_name: str
    venue: str
    city: str
    country: str

    conference_date: date
    publication_date: date | None = None

    publisher: str | None = None
    proceedings_name: str | None = None

    isbn: str | None = None
    issn: str | None = None

    outcome: ConferenceOutcome
    remarks: str | None = None


class PublicationConferenceUpdate(BaseModel):
    conference_name: str | None = None
    venue: str | None = None
    city: str | None = None
    country: str | None = None

    conference_date: date | None = None
    publication_date: date | None = None

    publisher: str | None = None
    proceedings_name: str | None = None

    isbn: str | None = None
    issn: str | None = None

    outcome: ConferenceOutcome | None = None
    remarks: str | None = None


class PublicationConferenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    publication_id: UUID

    conference_name: str
    venue: str
    city: str
    country: str

    conference_date: date
    publication_date: date | None

    publisher: str | None
    proceedings_name: str | None

    isbn: str | None
    issn: str | None

    outcome: ConferenceOutcome
    remarks: str | None