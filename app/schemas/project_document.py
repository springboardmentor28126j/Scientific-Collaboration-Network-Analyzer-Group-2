from pydantic import BaseModel
from datetime import datetime


class ProjectDocumentBase(BaseModel):

    project_id: int
    uploaded_by: int
    file_name: str
    file_type: str | None = None
    file_url: str | None = None
    description: str | None = None


class ProjectDocumentCreate(ProjectDocumentBase):
    pass


class ProjectDocumentUpdate(BaseModel):

    file_name: str | None = None
    file_type: str | None = None
    file_url: str | None = None
    description: str | None = None


class ProjectDocumentResponse(ProjectDocumentBase):

    id: int
    uploaded_at: datetime

    class Config:
        from_attributes = True