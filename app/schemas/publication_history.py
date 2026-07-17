from datetime import datetime
import uuid

from pydantic import BaseModel, ConfigDict

from app.models.publication_history import PublicationHistoryAction
from app.schemas.user import UserRead


class HistoryUserRead(BaseModel):
    id: uuid.UUID
    full_name: str

    model_config = ConfigDict(from_attributes=True)


class PublicationHistoryRead(BaseModel):
    id: uuid.UUID
    publication_id: uuid.UUID

    action: PublicationHistoryAction
    description: str

    created_at: datetime

    user: HistoryUserRead | None

    model_config = ConfigDict(
        from_attributes=True,
    )
