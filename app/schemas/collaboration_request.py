from pydantic import BaseModel
from datetime import datetime


class CollaborationRequestBase(BaseModel):

    sender_id: int
    receiver_id: int
    paper_id: int
    message: str | None = None


class CollaborationRequestCreate(CollaborationRequestBase):
    pass


class CollaborationRequestUpdate(BaseModel):

    status: str

class CollaborationRequestResponse(CollaborationRequestBase):

    id: int

    sender_name: str
    receiver_name: str

    paper_title: str

    status: str
    created_at: datetime

    class Config:
        from_attributes = True