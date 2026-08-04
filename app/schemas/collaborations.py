from uuid import UUID
from pydantic import BaseModel, ConfigDict

from app.models.collaboration import CollaborationStatus


class CollaborationCreate(BaseModel):
    receiver_id: UUID


class CollaborationUpdate(BaseModel):
    status: CollaborationStatus


class CollaborationResponse(BaseModel):
    id: UUID
    sender_id: UUID
    receiver_id: UUID
    status: CollaborationStatus

    model_config = ConfigDict(from_attributes=True)