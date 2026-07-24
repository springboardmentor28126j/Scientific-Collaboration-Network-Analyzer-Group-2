from pydantic import BaseModel
from datetime import date


class ConferenceBase(BaseModel):
    conference_name: str
    organizer: str
    venue: str
    country: str
    conference_date: date
    submission_deadline: date
    registration_deadline: date
    registration_fee: int
    conference_type: str
    website: str | None = None
    description: str | None = None
    topics: str | None = None
    status: str = "Upcoming"


class ConferenceCreate(ConferenceBase):
    pass


class ConferenceUpdate(BaseModel):
    conference_name: str | None = None
    organizer: str | None = None
    venue: str | None = None
    country: str | None = None
    conference_date: date | None = None
    submission_deadline: date | None = None
    registration_deadline: date | None = None
    registration_fee: int | None = None
    conference_type: str | None = None
    website: str | None = None
    description: str | None = None
    topics: str | None = None
    status: str | None = None


class ConferenceResponse(ConferenceBase):
    id: int
    researcher_id: int
    banner_image: str | None = None
    brochure_pdf: str | None = None

    model_config = {
        "from_attributes": True
    }