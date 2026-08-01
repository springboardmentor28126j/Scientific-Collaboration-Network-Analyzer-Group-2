from pydantic import BaseModel
from datetime import datetime


class ProjectMemberBase(BaseModel):

    project_id: int

    researcher_id: int

    role: str = "Co-Researcher"


class ProjectMemberCreate(ProjectMemberBase):
    pass


class ProjectMemberUpdate(BaseModel):

    role: str


class ProjectMemberResponse(ProjectMemberBase):

    id: int

    joined_at: datetime

    class Config:

        from_attributes = True