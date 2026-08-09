from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SessionCreate(BaseModel):
    title: str
    description: str | None = None
    start_time: datetime
    end_time: datetime | None = None
    room: str | None = None
    speaker_participation_id: int | None = None


class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conference_id: int
    title: str
    description: str | None
    start_time: datetime
    end_time: datetime | None
    room: str | None
    speaker_participation_id: int | None
    speaker_email: str | None = None
    speaker_role: str | None = None
    