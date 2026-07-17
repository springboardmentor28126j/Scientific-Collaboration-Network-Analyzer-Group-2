import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.review_assignment import ReviewAssignmentStatus
from app.schemas.common import ORMBase


class ReviewAssignmentCreate(BaseModel):
    reviewer_ids: list[uuid.UUID]


class ReviewAssignmentRead(ORMBase):
    id: uuid.UUID
    publication_id: uuid.UUID

    reviewer_id: uuid.UUID
    reviewer_name: str
    reviewer_email: str

    assigned_by: uuid.UUID

    status: ReviewAssignmentStatus

    assigned_at: datetime
    completed_at: datetime | None
