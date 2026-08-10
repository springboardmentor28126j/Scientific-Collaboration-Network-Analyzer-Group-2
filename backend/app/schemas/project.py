from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.project import ProjectRole, ProjectStatus


class ProjectMemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    researcher_id: int
    role_in_project: ProjectRole
    joined_at: datetime


class ProjectMemberAdd(BaseModel):
    researcher_id: int
    role_in_project: ProjectRole = ProjectRole.MEMBER


class ProjectBase(BaseModel):
    title: str
    description: str | None = None
    status: ProjectStatus = ProjectStatus.PLANNED
    start_date: date | None = None
    end_date: date | None = None
    institution_id: int | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ProjectBase):
    pass


class ProjectOut(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_researcher_id: int
    created_at: datetime
    updated_at: datetime
    members: list[ProjectMemberOut] = []
