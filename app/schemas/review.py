import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase
from app.models.review import ReviewDecision


class ReviewCreate(BaseModel):
    assignment_id: uuid.UUID
    decision: ReviewDecision
    score: int = Field(ge=1, le=10)

    strengths: str
    weaknesses: str
    comments: str
    recommendation: str


class ReviewRead(ORMBase):
    id: uuid.UUID

    assignment_id: uuid.UUID

    decision: ReviewDecision

    score: int

    strengths: str
    weaknesses: str
    comments: str
    recommendation: str

    submitted_at: datetime
