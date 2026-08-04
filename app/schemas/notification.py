import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class NotificationType(str, Enum):
    COLLABORATION = "Collaboration"
    CONFERENCE = "Conference"
    PUBLICATION = "Publication"
    SYSTEM = "System"


class NotificationBase(BaseModel):
    title: str
    message: str
    notification_type: NotificationType


class NotificationCreate(NotificationBase):
    user_id: uuid.UUID


class NotificationResponse(NotificationBase):
    id: uuid.UUID
    user_id: uuid.UUID
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True