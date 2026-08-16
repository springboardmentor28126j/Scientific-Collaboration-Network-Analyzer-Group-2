from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.conference import ParticipationRole, SubmissionStatus, ConferenceStatus


class ConferenceCreate(BaseModel):
    name: str
    description: str | None = None
    start_date: date
    end_date: date
    location: str | None = None
    organizing_institution_id: int | None = None
    website_url: str | None = None


class ConferenceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    location: str | None = None
    organizing_institution_id: int | None = None
    website_url: str | None = None
    status: ConferenceStatus | None = None


class ConferenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    conference_id: int
    name: str
    description: str | None
    start_date: date
    end_date: date
    location: str | None
    organizing_institution_id: int | None
    website_url: str | None
    status: ConferenceStatus
    created_at: datetime


class ParticipationCreate(BaseModel):
    role: ParticipationRole
    presentation_title: str | None = None
    publication_id: int | None = None


class ParticipationUpdate(BaseModel):
    role: ParticipationRole | None = None
    submission_status: SubmissionStatus | None = None
    presentation_title: str | None = None
    publication_id: int | None = None


class ParticipationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    participation_id: int
    conference_id: int
    researcher_id: int
    researcher_name: str
    role: ParticipationRole
    submission_status: SubmissionStatus
    presentation_title: str | None
    publication_id: int | None
    registered_at: datetime
