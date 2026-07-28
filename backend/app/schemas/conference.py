from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, computed_field, model_validator

from app.models.conference import ConferenceType

from app.models.participation import ParticipationRole, ParticipationStatus


class ConferenceBase(BaseModel):
    name: str
    description: str | None = None
    location: str | None = None
    website_link: str | None = None
    conference_type: ConferenceType | None = None
    start_date: date | None = None
    end_date: date | None = None
    institution_id: int | None = None


class ConferenceCreate(ConferenceBase):
    # Required going forward: every new conference must belong to the
    # institution hosting it (see create_conference for the ownership check).
    institution_id: int


class ConferenceUpdate(ConferenceBase):
    pass


class ConferenceOut(ConferenceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_by: int | None
    created_at: datetime


class ParticipationCreate(BaseModel):
    role: ParticipationRole = ParticipationRole.ATTENDEE
    presentation_title: str | None = None

    @model_validator(mode="after")
    def _self_registration_roles_only(self) -> "ParticipationCreate":
        if self.role not in (ParticipationRole.ATTENDEE, ParticipationRole.PRESENTER):
            raise ValueError(
                "You can only self-register as Attendee or Presenter. "
                "Organizer/Reviewer roles are assigned by the conference organizer."
            )
        return self


class ParticipationRoleUpdate(BaseModel):
    role: ParticipationRole


class ParticipationStatusUpdate(BaseModel):
    status: ParticipationStatus


class ParticipationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    researcher_id: int
    conference_id: int
    role: ParticipationRole
    presentation_title: str | None
    status: ParticipationStatus
    stored_filename: str | None = None
    original_filename: str | None = None
    registered_at: datetime | None = None

    @computed_field
    @property
    def file_url(self) -> str | None:
        if self.stored_filename:
            return f"/uploads/conference_presentations/{self.stored_filename}"
        return None


class ParticipationWithConference(ParticipationOut):
    conference: ConferenceOut