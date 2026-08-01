from pydantic import BaseModel
from datetime import datetime


class NotificationBase(BaseModel):

    researcher_id: int
    title: str
    message: str


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):

    is_read: bool


class NotificationResponse(NotificationBase):

    id: int
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True