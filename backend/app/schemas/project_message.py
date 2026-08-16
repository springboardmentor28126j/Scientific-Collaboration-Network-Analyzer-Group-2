from datetime import datetime

from pydantic import BaseModel, field_validator


class ProjectMessageCreate(BaseModel):
    body: str

    @field_validator("body")
    @classmethod
    def not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Message can't be empty")
        if len(v) > 5000:
            raise ValueError("Message is too long (max 5000 characters)")
        return v


class ProjectMessageOut(BaseModel):
    project_message_id: int
    project_id: int
    sender_id: int
    sender_name: str
    body: str
    created_at: datetime


class ProjectMessageListResponse(BaseModel):
    items: list[ProjectMessageOut]
    total: int