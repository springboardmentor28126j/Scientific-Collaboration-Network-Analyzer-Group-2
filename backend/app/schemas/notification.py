from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class NotificationCreate(BaseModel):
    message: str
    type: Optional[str] = None


class NotificationOut(NotificationCreate):
    id: int
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True