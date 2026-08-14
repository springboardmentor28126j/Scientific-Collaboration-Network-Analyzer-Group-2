from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.validators import validate_password_strength


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    turnstile_token: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def check_password_strength(cls, v: str) -> str:
        return validate_password_strength(v)


class VerifyTokenRequest(BaseModel):
    """Used for institution-admin email verification — the admin already
    set a password at self-registration, so only the token is needed."""

    token: str


class VerifyInviteRequest(BaseModel):
    """
    Used for researcher/reviewer invite verification. Unlike the
    institution admin, an invited user has no password yet — the
    institution admin only supplied email/name/description when creating
    the account — so the invited user sets their password here, at
    verification time.
    """

    token: str
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def check_password_strength(cls, v: str) -> str:
        return validate_password_strength(v)
