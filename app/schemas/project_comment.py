from pydantic import BaseModel
from datetime import datetime


class ProjectCommentBase(BaseModel):

    project_id: int
    researcher_id: int
    comment: str


class ProjectCommentCreate(ProjectCommentBase):
    pass


class ProjectCommentUpdate(BaseModel):

    comment: str


class ProjectCommentResponse(ProjectCommentBase):

    id: int
    created_at: datetime

    class Config:
        from_attributes = True