from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.api.dependencies import get_db, get_current_user

from app.schemas.auth import (
    LoginRequest,
    Token,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)

from app.schemas.user import (
    UserCreate,
    UserResponse,
)

from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


class ResendVerificationRequest(BaseModel):
    email: EmailStr


# ------------------------------------------------------------------
# Register
# ------------------------------------------------------------------

@router.post(
    "/register",
    response_model=UserResponse,
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    try:
        return AuthService.register(
            db,
            user,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


# ------------------------------------------------------------------
# Login
# ------------------------------------------------------------------

@router.post(
    "/login",
    response_model=Token,
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    try:
        token = AuthService.login(
            db,
            request.email,
            request.password,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=403,
            detail=str(e),
        )

    if token is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


# ------------------------------------------------------------------
# Swagger Login
# ------------------------------------------------------------------

@router.post(
    "/token",
    response_model=Token,
)
def login_for_swagger(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    try:
        token = AuthService.login(
            db,
            form_data.username,
            form_data.password,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=403,
            detail=str(e),
        )

    if token is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


# ------------------------------------------------------------------
# Verify Email
# ------------------------------------------------------------------

@router.get("/verify-email")
def verify_email(
    token: str,
    db: Session = Depends(get_db),
):
    try:
        AuthService.verify_email(
            db,
            token,
        )

        return {
            "message": "Email verified successfully."
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


# ------------------------------------------------------------------
# Resend Verification
# ------------------------------------------------------------------

@router.post("/resend-verification")
def resend_verification(
    request: ResendVerificationRequest,
    db: Session = Depends(get_db),
):
    try:
        return AuthService.resend_verification(
            db,
            request.email,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


# ------------------------------------------------------------------
# Forgot Password
# ------------------------------------------------------------------

@router.post("/forgot-password")
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    try:
        return AuthService.forgot_password(
            db,
            request.email,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


# ------------------------------------------------------------------
# Reset Password
# ------------------------------------------------------------------

@router.post("/reset-password")
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    try:
        return AuthService.reset_password(
            db,
            request.token,
            request.password,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


# ------------------------------------------------------------------
# Current User
# ------------------------------------------------------------------

@router.get("/me")
def me(
    current_user=Depends(get_current_user),
):
    return current_user
