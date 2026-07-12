from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InstitutionBase(BaseModel):
    name: str
    type: str | None = None
    address: str | None = None
    website: str | None = None


class InstitutionCreate(InstitutionBase):
    pass


class InstitutionUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    address: str | None = None
    website: str | None = None


class InstitutionRead(InstitutionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
