from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict, Field

from app.models.user import UserRole, AffiliationStatus

class GoogleSignInRequest(BaseModel):
    id_token: str
    role: UserRole | None = None          # only needed the first time (new account)
    institution_id: int | None = None      # only needed for institution_admin/reviewer on first sign-in


class GoogleSignInResult(BaseModel):
    """
    Either a normal token pair (existing/linked account), or a signal that
    the frontend needs to collect a role before the account can be created.
    """
    needs_role_selection: bool = False
    email: EmailStr | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str = "bearer"

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    role: UserRole
    institution_id: int | None = None
    institution_name: str | None = None
    website: str | None = None
    domain: str | None = None
    address: str | None = None
    official_email: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    email: EmailStr
    role: UserRole
    institution_id: int | None
    is_active: bool
    affiliation_status: AffiliationStatus
    created_at: datetime


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None


class InstitutionSelect(BaseModel):
    institution_id: int


class UserAdminUpdate(BaseModel):
    role: UserRole | None = None
    is_active: bool | None = None


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class MessageResponse(BaseModel):
    message: str
