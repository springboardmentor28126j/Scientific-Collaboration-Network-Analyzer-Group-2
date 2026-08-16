from datetime import datetime

from pydantic import BaseModel, field_validator


class MessageCreate(BaseModel):
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


class MessageOut(BaseModel):
    message_id: int
    collaboration_id: int
    sender_id: int
    sender_name: str
    body: str
    is_read: bool
    created_at: datetime


class MessageListResponse(BaseModel):
    items: list[MessageOut]
    total: int


class UnreadMessageCountOut(BaseModel):
    unread_count: int