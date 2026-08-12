from datetime import datetime
from pydantic import BaseModel


class AuditLogCreate(BaseModel):

    user_id: int
    action: str
    module: str
    description: str


class AuditLogResponse(BaseModel):

    id: int
    user_id: int
    action: str
    module: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True