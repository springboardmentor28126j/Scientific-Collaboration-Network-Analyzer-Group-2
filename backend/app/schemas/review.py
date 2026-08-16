from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.review import ReviewTargetType, ReviewStatus, ReviewRecommendation


class ReviewAssign(BaseModel):
    target_type: ReviewTargetType
    target_id: int
    reviewer_id: int


class ReviewSubmit(BaseModel):
    score: int | None = Field(default=None, ge=1, le=10)
    comments: str | None = None
    recommendation: ReviewRecommendation


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    review_id: int
    target_type: ReviewTargetType
    target_id: int
    reviewer_id: int | None  # masked (None) for viewers who shouldn't see who's reviewing -- see reviews.py
    assigned_by: int | None
    status: ReviewStatus
    score: int | None
    comments: str | None
    recommendation: ReviewRecommendation | None
    assigned_at: datetime
    responded_at: datetime | None
    completed_at: datetime | None
