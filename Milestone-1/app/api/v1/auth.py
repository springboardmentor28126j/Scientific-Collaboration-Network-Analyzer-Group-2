from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_auth_service
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    RefreshRequest,
    ResetPasswordRequest,
    TokenPair,
    VerifyInviteRequest,
    VerifyTokenRequest,
)
from app.schemas.common import Message
from app.schemas.user import UserMe
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/login",
    response_model=TokenPair,
    summary="Log in with email + password",
    description=(
        "OAuth2-password-flow-compatible login. Use your email as the "
        "`username` field. Works identically for institution admins, "
        "researchers, and reviewers — access is gated purely by "
        "`is_verified` + `is_active` (plus the parent institution being "
        "active), not by role."
    ),
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenPair:
    user = await auth_service.authenticate(form_data.username, form_data.password)
    return auth_service.issue_token_pair(user)


@router.post(
    "/refresh",
    response_model=TokenPair,
    summary="Exchange a refresh token for a new access token",
)
async def refresh(
    payload: RefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenPair:
    return await auth_service.refresh_access_token(payload.refresh_token)


@router.get("/me", response_model=UserMe, summary="Get the currently authenticated user")
async def read_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.post(
    "/verify-email",
    response_model=Message,
    summary="Verify an institution admin's email (auto-activates the account)",
)
async def verify_email(
    payload: VerifyTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> Message:
    await auth_service.verify_email_token(payload.token)
    return Message(detail="Email verified. Your account is now active — you can log in.")


@router.post(
    "/verify-invite",
    response_model=Message,
    summary="Verify a researcher/reviewer invite and set an initial password",
)
async def verify_invite(
    payload: VerifyInviteRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> Message:
    await auth_service.verify_invite_token(payload.token, payload.password)
    return Message(detail="Account verified and activated. You can now log in.")


@router.post(
    "/forgot-password",
    response_model=Message,
    status_code=status.HTTP_200_OK,
    summary="Request a password reset link",
    description=(
        "Available to any verified user (institution admin, researcher, "
        "or reviewer). Always returns a generic success message, whether "
        "or not the email exists, to avoid leaking which addresses are "
        "registered."
    ),
)
async def forgot_password(
    payload: ForgotPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> Message:
    await auth_service.request_password_reset(payload.email)
    return Message(
        detail="If an account with that email exists, a password reset link has been sent."
    )


@router.post(
    "/reset-password",
    response_model=Message,
    summary="Reset a password using a token from the forgot-password email",
)
async def reset_password(
    payload: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> Message:
    await auth_service.reset_password(payload.token, payload.new_password)
    return Message(detail="Password reset successfully. You can now log in.")
