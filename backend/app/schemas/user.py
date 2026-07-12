from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole
from app.schemas.institution import InstitutionRead
from app.schemas.researcher_profile import ResearcherProfileRead


class UserBase(BaseModel):
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    password: str = Field(min_length=8)
    role: UserRole = UserRole.RESEARCHER
    institution_id: int | None = None


class UserUpdate(BaseModel):
    full_name: str | None = None
    institution_id: int | None = None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: UserRole
    institution_id: int | None
    is_active: bool
    created_at: datetime


class UserDetailRead(UserRead):
    institution: InstitutionRead | None = None
    researcher_profile: ResearcherProfileRead | None = None
