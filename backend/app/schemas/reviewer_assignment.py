from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator


class ReviewerAssignmentCreate(BaseModel):
    reviewer_user_id: int
    # Provide exactly one of these two.
    institution_id: int | None = None
    publication_id: int | None = None

    @model_validator(mode="after")
    def _exactly_one_scope(self) -> "ReviewerAssignmentCreate":
        if (self.institution_id is None) == (self.publication_id is None):
            raise ValueError(
                "Provide exactly one of institution_id or publication_id"
            )
        return self


class ReviewerAssignmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reviewer_user_id: int
    institution_id: int | None
    publication_id: int | None
    assigned_by: int
    created_at: datetime
