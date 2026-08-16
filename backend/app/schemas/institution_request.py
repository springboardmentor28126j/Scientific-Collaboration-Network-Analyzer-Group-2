from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InstitutionRequestCreate(BaseModel):
    institution_name: str
    website: str | None = None
    domain: str | None = None
    address: str | None = None
    official_email: str | None = None


class InstitutionRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    request_id: int
    institution_name: str
    website: str | None
    domain: str | None
    address: str | None
    official_email: str | None
    status: str
    requested_by_user_id: int
    created_at: datetime
