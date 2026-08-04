from uuid import UUID
from datetime import date

from pydantic import BaseModel, ConfigDict


class ConferenceBase(BaseModel):
    title: str
    location: str | None = None
    conference_date: date | None = None
    description: str | None = None


class ConferenceCreate(ConferenceBase):
    pass


class ConferenceUpdate(BaseModel):
    title: str | None = None
    location: str | None = None
    conference_date: date | None = None
    description: str | None = None


class ConferenceResponse(ConferenceBase):
    id: UUID
    participant_count: int = 0

    model_config = ConfigDict(from_attributes=True)
