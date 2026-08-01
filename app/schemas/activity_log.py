from pydantic import BaseModel
from datetime import datetime


class ActivityLogBase(BaseModel):

    project_id: int

    researcher_id: int

    activity: str

    activity_type: str


class ActivityLogCreate(ActivityLogBase):
    pass


class ActivityLogResponse(ActivityLogBase):

    id: int

    created_at: datetime

    class Config:

        from_attributes = True