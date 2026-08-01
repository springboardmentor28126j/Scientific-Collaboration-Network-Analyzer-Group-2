from pydantic import BaseModel
from datetime import date, datetime


class ProjectMilestoneBase(BaseModel):

    project_id: int

    title: str

    description: str | None = None

    deadline: date

    status: str = "Pending"


class ProjectMilestoneCreate(ProjectMilestoneBase):
    pass


class ProjectMilestoneUpdate(BaseModel):

    title: str | None = None

    description: str | None = None

    deadline: date | None = None

    status: str | None = None


class ProjectMilestoneResponse(ProjectMilestoneBase):

    id: int

    created_at: datetime

    updated_at: datetime

    class Config:

        from_attributes = True