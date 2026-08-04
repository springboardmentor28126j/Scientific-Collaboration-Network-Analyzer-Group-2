from uuid import UUID
from pydantic import BaseModel, ConfigDict


class InstitutionBase(BaseModel):
    name: str
    abbreviation: str | None = None
    website: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None


class InstitutionCreate(InstitutionBase):
    pass


class InstitutionUpdate(BaseModel):
    name: str | None = None
    abbreviation: str | None = None
    website: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None


class InstitutionResponse(InstitutionBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
