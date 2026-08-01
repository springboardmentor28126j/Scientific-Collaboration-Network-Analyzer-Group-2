from pydantic import BaseModel
from datetime import date, datetime


class ProjectTaskBase(BaseModel):

    project_id: int

    milestone_id: int

    assigned_to: int

    title: str

    description: str | None = None

    deadline: date

    priority: str = "Medium"

    status: str = "Pending"


class ProjectTaskCreate(ProjectTaskBase):
    pass


class ProjectTaskUpdate(BaseModel):

    title: str | None = None

    description: str | None = None

    deadline: date | None = None

    priority: str | None = None

    status: str | None = None

    assigned_to: int | None = None


class ProjectTaskResponse(ProjectTaskBase):

    id: int

    created_at: datetime

    updated_at: datetime

    class Config:

        from_attributes = True