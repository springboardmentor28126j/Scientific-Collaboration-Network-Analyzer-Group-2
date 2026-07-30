from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CollaborationBase(BaseModel):
    researcher_1_id: int
    researcher_2_id: int
    paper_id: int
    collaboration_year: int
    requested_by: Optional[int] = None


class CollaborationCreate(CollaborationBase):
    pass


class CollaborationResponse(CollaborationBase):
    id: int
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True