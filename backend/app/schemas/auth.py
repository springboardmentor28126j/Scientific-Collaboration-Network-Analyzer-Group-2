from pydantic import BaseModel, EmailStr


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class MfaVerifyRequest(BaseModel):
    pre_auth_token: str
    code: str


class MfaResendRequest(BaseModel):
    pre_auth_token: str
