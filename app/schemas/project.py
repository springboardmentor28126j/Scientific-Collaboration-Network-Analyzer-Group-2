from pydantic import BaseModel
from datetime import date, datetime


class ProjectBase(BaseModel):

    title: str

    description: str | None = None

    start_date: date

    end_date: date | None = None

    status: str = "Active"

    project_lead_id: int

    institution_id: int


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):

    title: str | None = None

    description: str | None = None

    start_date: date | None = None

    end_date: date | None = None

    status: str | None = None

    project_lead_id: int | None = None

    institution_id: int | None = None


class ProjectResponse(ProjectBase):

    id: int

    created_at: datetime

    updated_at: datetime

    class Config:

        from_attributes = True