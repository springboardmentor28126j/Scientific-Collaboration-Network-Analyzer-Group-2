from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.project import ProjectMemberRole, ProjectMemberStatus, ProjectStatus


class ProjectCreate(BaseModel):
    title: str
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class ProjectUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: ProjectStatus | None = None
    start_date: date | None = None
    end_date: date | None = None


class ProjectMemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
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

    id: int
    title: str
    description: str | None
    status: ProjectStatus
    lead_researcher_id: int
    institution_id: int | None
    start_date: date | None
    end_date: date | None
    created_at: datetime
    updated_at: datetime


class ProjectDetailOut(ProjectOut):
    members: list[ProjectMemberOut] = []