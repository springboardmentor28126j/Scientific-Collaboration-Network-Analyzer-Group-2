from pydantic import BaseModel
from datetime import date, datetime


class ProjectTimelineBase(BaseModel):

    project_id: int
    event_title: str
    description: str | None = None
    event_date: date
    event_type: str


class ProjectTimelineCreate(ProjectTimelineBase):
    pass


class ProjectTimelineUpdate(BaseModel):

    event_title: str | None = None
    description: str | None = None
    event_date: date | None = None
    event_type: str | None = None


class ProjectTimelineResponse(ProjectTimelineBase):

    id: int
    created_at: datetime

    class Config:
        from_attributes = True