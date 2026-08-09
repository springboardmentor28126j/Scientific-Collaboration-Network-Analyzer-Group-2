from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MessageSenderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    body: str
    created_at: datetime
    sender_researcher_id: int
    sender_email: str
    is_mine: bool


class MessageCreate(BaseModel):
    body: str


class ConversationOut(BaseModel):
    id: int
    scope_type: str  # "project" or "collaboration"
    scope_id: int
    scope_label: str
    messages: list[MessageOut]


class ConversationSummary(BaseModel):
    conversation_id: int
    scope_type: str
    scope_id: int
    scope_label: str
    last_message_preview: str | None
    last_message_at: datetime | None
    unread_count: int


class InboxOut(BaseModel):
    items: list[ConversationSummary]