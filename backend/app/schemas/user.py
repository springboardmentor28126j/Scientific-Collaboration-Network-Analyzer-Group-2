from pydantic import BaseModel, EmailStr, ConfigDict

from app.models.user import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole = UserRole.RESEARCHER
    institution_id: int | None = None  # required when role == INSTITUTION_ADMIN


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    role: UserRole
    is_active: bool
    is_verified: bool
    mfa_enabled: bool


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    mfa_required: bool = False
    pre_auth_token: str | None = None


class TokenPayload(BaseModel):
    sub: str | None = None


class GoogleSignInRequest(BaseModel):
    id_token: str
    role: UserRole | None = None
    institution_id: int | None = None


class GoogleSignInResult(BaseModel):
    access_token: str | None = None
    token_type: str = "bearer"
    needs_role_selection: bool = False
    pending_approval: bool = False
    message: str | None = None
    email: str | None = None