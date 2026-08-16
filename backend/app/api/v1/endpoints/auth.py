from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core import recaptcha as recaptcha_service
from app.core import redis_client
from app.core.config import settings
from app.core.dependencies import oauth2_scheme
from app.core.security import decode_token
from app.db.session import get_db
from app.schemas.user import UserRegister, UserOut, TokenPair, RefreshRequest
from app.services import user_service
from app.schemas.user import GoogleSignInRequest, GoogleSignInResult
from app.schemas.user import ResendVerificationRequest, MessageResponse, ForgotPasswordRequest, ResetPasswordRequest
from app.services import email_deliverability_service
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth", tags=["Authentication"])


class EmailCheckRequest(BaseModel):
    email: EmailStr


class EmailCheckResponse(BaseModel):
    checked: bool
    is_valid: bool | None
    reason: str | None


@router.post("/check-email-deliverability", response_model=EmailCheckResponse)
def check_email_deliverability(payload: EmailCheckRequest):
    result = email_deliverability_service.check_email_deliverability(payload.email)
    return EmailCheckResponse(**result)


@router.post("/google", response_model=GoogleSignInResult)
def google_sign_in(payload: GoogleSignInRequest, db: Session = Depends(get_db)):
    try:
        result = user_service.google_sign_in(
            db, token=payload.id_token, role=payload.role, institution_id=payload.institution_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if result is None:
        # New account, no role chosen yet -- ask the frontend to collect one.
        from google.oauth2 import id_token as google_id_token
        from google.auth.transport import requests as google_requests
        from app.core.config import settings

        try:
            decoded = google_id_token.verify_oauth2_token(
                payload.id_token,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID,
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Google ID token",
            ) from exc

        return GoogleSignInResult(needs_role_selection=True, email=decoded["email"])

    access_token, refresh_token = result
    return GoogleSignInResult(access_token=access_token, refresh_token=refresh_token)


@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    user = user_service.register_user(
        db, email=payload.email, password=payload.password, role=payload.role,
        institution_id=payload.institution_id,
        institution_name=payload.institution_name,
        website=payload.website,
        domain=payload.domain,
        address=payload.address,
        official_email=payload.official_email,
    )
    return user


@router.post("/login", response_model=TokenPair)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    recaptcha_token: str | None = Form(None),
    db: Session = Depends(get_db),
):
    """
    Normal login only needs email + password. But once an email has racked
    up LOGIN_MAX_FAILED_ATTEMPTS failures within the tracking window, this
    starts refusing to even check the password again until a solved Google
    reCAPTCHA (recaptcha_token, the "g-recaptcha-response" the widget
    produces) is presented alongside the credentials -- this is what slows
    down scripted credential-stuffing against a single account without
    touching accounts that are simply typing their password wrong once or
    twice.
    """
    # OAuth2PasswordRequestForm uses "username" as the field name; we treat it as email.
    email = form_data.username

    if redis_client.get_failed_login_count(email) >= settings.LOGIN_MAX_FAILED_ATTEMPTS:
        if not recaptcha_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "captcha_required",
                    "message": "Too many failed login attempts. Please solve the CAPTCHA to continue.",
                },
            )
        if not recaptcha_service.verify_recaptcha(recaptcha_token, remote_ip=request.client.host if request.client else None):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "captcha_invalid",
                    "message": "That CAPTCHA verification failed. Please try again.",
                },
            )

    try:
        user = user_service.authenticate_user(db, email=email, password=form_data.password)
    except HTTPException:
        window_seconds = settings.LOGIN_FAILED_ATTEMPTS_WINDOW_MINUTES * 60
        redis_client.record_failed_login(email, window_seconds)
        raise

    redis_client.reset_failed_login(email)
    access_token, refresh_token = user_service.issue_tokens(user)
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    # Refresh tokens are rotated on every use: the old one is revoked in
    # Redis and a brand new access + refresh pair is returned. Reusing an
    # already-exchanged refresh token now fails, which limits the damage
    # if one is ever stolen.
    new_access_token, new_refresh_token = user_service.refresh_access_token(db, payload.refresh_token)
    return TokenPair(access_token=new_access_token, refresh_token=new_refresh_token)


@router.get("/verify-email", response_model=MessageResponse)
def verify_email(token: str, db: Session = Depends(get_db)):
    user_service.verify_email(db, token)
    return MessageResponse(message="Email verified successfully. You can now log in.")


@router.post("/resend-verification", response_model=MessageResponse)
def resend_verification(payload: ResendVerificationRequest, db: Session = Depends(get_db)):
    user_service.resend_verification_email(db, payload.email)
    # Same response whether or not the account exists/needs it -- avoids
    # leaking which emails are registered.
    return MessageResponse(message="If that email needs verification, a new link has been sent.")


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user_service.request_password_reset(db, payload.email)
    # Same response regardless of whether the email is registered, whether
    # it's a Google-only account, etc. -- avoids leaking account existence.
    return MessageResponse(message="If that email has an account, a password reset link has been sent.")


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    user_service.reset_password(db, payload.token, payload.new_password)
    return MessageResponse(message="Password reset successfully. You can now log in with your new password.")


@router.post("/logout", status_code=204)
def logout(payload: RefreshRequest | None = None, token: str = Depends(oauth2_scheme)):
    """
    Revokes the caller's current access session in Redis immediately, and
    the refresh session too if a refresh token is supplied in the body.
    Unlike a purely stateless JWT logout, tokens stop working right away
    instead of remaining valid until they naturally expire.
    """
    access_payload = decode_token(token)
    access_jti = access_payload.get("jti")
    refresh_token = payload.refresh_token if payload else None
    user_service.logout_user(access_jti=access_jti, refresh_token=refresh_token)
    return None
