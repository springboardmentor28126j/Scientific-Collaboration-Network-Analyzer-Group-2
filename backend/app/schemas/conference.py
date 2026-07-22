from pydantic import BaseModel
from datetime import date
from typing import Optional


class ConferenceCreate(BaseModel):
    name: str
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ConferenceOut(ConferenceCreate):
    id: int

    class Config:
        from_attributes = True


class ParticipationCreate(BaseModel):
    conference_id: int
    researcher_id: int
    presentation_title: Optional[str] = None


class ParticipationOut(ParticipationCreate):
    id: int

    class Config:
        from_attributes = True