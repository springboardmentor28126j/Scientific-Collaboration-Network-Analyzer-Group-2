import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import UserRole
from app.schemas.common import ORMBase


class UserCreateByInstitution(BaseModel):
    """Used by an institution admin to create a Researcher or Reviewer."""

    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    role: UserRole
    description: str | None = Field(default=None, max_length=1000)

    @field_validator("role")
    @classmethod
    def role_must_be_researcher_or_reviewer(cls, v: UserRole) -> UserRole:
        if v not in (UserRole.RESEARCHER, UserRole.REVIEWER):
            raise ValueError("role must be RESEARCHER or REVIEWER")
        return v


class UserRead(ORMBase):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: UserRole
    description: str | None
    institution_id: uuid.UUID | None
    is_verified: bool
    is_active: bool
    created_at: datetime


class UserMe(UserRead):
    """What /auth/me returns — same shape as UserRead for now, kept
    separate so it can diverge later without touching the admin-facing
    UserRead schema."""
