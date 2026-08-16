from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.project import ProjectStatus, ProjectMemberRole
from app.models.project import ProjectStatus, ProjectMemberRole, ProjectMemberStatus

class ProjectCreate(BaseModel):
    title: str
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    # Only used when a System Admin or Institution Admin creates a project on
    # behalf of a researcher. A researcher creating their own project always
    # becomes the lead automatically -- this field is ignored for them.
    lead_researcher_id: int | None = None


class ProjectUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: ProjectStatus | None = None
    start_date: date | None = None
    end_date: date | None = None


class ProjectMemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_member_id: int
    project_id: int
    researcher_id: int
    role: ProjectMemberRole
    status: ProjectMemberStatus
    invited_by_id: int | None
    responded_at: datetime | None
    joined_at: datetime


class ProjectMemberAdd(BaseModel):
    researcher_id: int

class ProjectMemberRespond(BaseModel):
    accept: bool

class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id: int
    title: str
    description: str | None
    status: ProjectStatus
    lead_researcher_id: int
    institution_id: int | None
    start_date: date | None
    end_date: date | None
    created_at: datetime
    updated_at: datetime
