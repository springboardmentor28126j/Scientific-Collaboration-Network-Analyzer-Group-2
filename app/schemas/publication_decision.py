from enum import StrEnum

from pydantic import BaseModel, Field


class EditorialDecision(StrEnum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    REVISION_REQUIRED = "REVISION_REQUIRED"


class PublicationDecisionCreate(BaseModel):
    decision: EditorialDecision

    editor_note: str = Field(
        min_length=10,
        max_length=5000,
    )
