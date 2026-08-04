from uuid import UUID
from pydantic import BaseModel, ConfigDict


class ConferenceRegistrationResponse(BaseModel):
    id: UUID
    conference_id: UUID
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)
