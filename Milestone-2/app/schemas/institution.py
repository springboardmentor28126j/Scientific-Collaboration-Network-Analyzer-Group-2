import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.validators import validate_password_strength
from app.schemas.common import ORMBase


class InstitutionRegister(BaseModel):
    """
    Fields for institution self-registration. The logo file itself is sent
    as multipart form data alongside this (see api/v1/institutions.py) —
    it isn't part of the JSON body since file uploads use `UploadFile`.
    """

    name: str = Field(min_length=1, max_length=255)
    address: str = Field(min_length=1, max_length=500)
    admin_full_name: str = Field(min_length=1, max_length=255)
    admin_email: EmailStr
    admin_password: str = Field(min_length=8, max_length=128)

    @field_validator("admin_password")
    @classmethod
    def check_password_strength(cls, v: str) -> str:
        return validate_password_strength(v)


class InstitutionRead(ORMBase):
    id: uuid.UUID
    name: str
    address: str
    logo_url: str | None
    is_active: bool
    created_at: datetime


class InstitutionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    address: str = Field(min_length=1, max_length=500)


class InstitutionUpdate(InstitutionCreate):
    logo_url: str | None = Field(default=None, max_length=1000)


class DepartmentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None


class DepartmentRead(DepartmentCreate, ORMBase):
    id: uuid.UUID
    institution_id: uuid.UUID
    created_at: datetime


class InstitutionUserRead(ORMBase):
    """Institution-scoped view of a researcher/reviewer — same as
    UserRead but imported separately to keep API contracts decoupled
    from the DB-facing schema module boundaries."""

    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: str
    description: str | None
    is_verified: bool
    is_active: bool
    created_at: datetime
