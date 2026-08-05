from pydantic import BaseModel
from typing import Optional


class CollaborationCreate(BaseModel):
    project_name: str
    institution_a: Optional[str] = None
    institution_b: Optional[str] = None
    description: Optional[str] = None


class CollaborationOut(CollaborationCreate):
    id: int

    class Config:
        from_attributes = True


class ProjectAssignmentCreate(BaseModel):
    collaboration_id: int
    researcher_id: int
    role_in_project: Optional[str] = None


class ProjectAssignmentOut(ProjectAssignmentCreate):
    id: int

    class Config:
        from_attributes = True