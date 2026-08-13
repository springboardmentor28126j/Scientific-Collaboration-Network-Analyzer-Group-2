import uuid
from datetime import datetime

from app.models.notification import NotificationType
from app.schemas.common import ORMBase


class NotificationRead(ORMBase):
    id: uuid.UUID

    notification_type: NotificationType

    title: str
    message: str

    publication_id: uuid.UUID | None

    is_read: bool

    created_at: datetime
