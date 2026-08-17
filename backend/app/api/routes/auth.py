from datetime import datetime, timedelta

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.routes.notifications import create_notification
from app.core.audit import log_audit
from app.core.config import settings
from app.core.email import send_email, render_email
from app.core.security import create_access_token, decode_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.auth_token import AuthToken, AuthTokenType
from app.models.institution import Institution
from app.models.researcher import Researcher
from app.models.user import User, UserRole
from app.schemas.auth import (
    ForgotPasswordRequest,
    ResendVerificationRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
)
from app.schemas.user import GoogleSignInRequest, GoogleSignInResult, Token, UserCreate, UserOut

router = APIRouter()


def _email_domain(email: str) -> str:
    return email.rsplit("@", 1)[-1].lower()


def _send_verification_email(db: Session, user: User) -> None:
    token = AuthToken.generate(user.id, AuthTokenType.EMAIL_VERIFICATION, hours_valid=48)
    db.add(token)
    db.commit()

    link = f"{settings.FRONTEND_URL}/verify-email?token={token.token}"
    send_email(
        to_email=user.email,
        subject="Verify your SCNA account",
        html_body=render_email(
            title="Verify your email",
            body_html="<p>Welcome to SCNA! Confirm your email address to activate your account.</p><p>This link is valid for 48 hours.</p>",
            cta_text="Verify Email",
            cta_link=link,
        ),
    )


def _send_mfa_otp_email(db: Session, user: User) -> AuthToken:
    otp = AuthToken.generate_otp(user.id)
    db.add(otp)
    db.commit()
    send_email(
        to_email=user.email,
        subject="Your SCNA login code",
        html_body=render_email(
            title="Your login code",
            body_html=f"<p>Your one-time login code is:</p><h2 style='letter-spacing:4px;'>{otp.token}</h2><p>This code expires in 10 minutes. If you didn't try to log in, you can ignore this email.</p>",
        ),
    )
    return otp


def _notify_system_admins(db: Session, message: str, link: str) -> None:
    admins = db.query(User).filter(User.role == UserRole.SYSTEM_ADMIN).all()
    for admin in admins:
        create_notification(
            db, recipient_user_id=admin.id, type="institution_admin_application", message=message, link=link
        )
        send_email(
            to_email=admin.email,
            subject="New Institution Admin application",
            html_body=render_email(
                title="New Institution Admin application",
                body_html=f"<p>{message}</p><p>Review it from the admin console.</p>",
                cta_text="Review Application",
                cta_link=f"{settings.FRONTEND_URL}{link}",
            ),
        )


def _create_institution_admin_application(
    db: Session,
    email: str,
    institution_id: int,
    password_hash: str | None,
    google_sub: str | None,
    pre_verified: bool,
) -> User:
    institution = db.query(Institution).filter(Institution.id == institution_id).first()
    if institution is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found")

    if _email_domain(email) != _email_domain(institution.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Your email domain doesn't match {institution.name}'s registered domain. "
                   f"Contact a System Admin if you believe this is an error.",
        )

    user = User(
        email=email,
        password_hash=password_hash,
        google_sub=google_sub,
        role=UserRole.INSTITUTION_ADMIN,
        is_active=False,
        is_verified=pre_verified,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    if not pre_verified:
        _send_verification_email(db, user)

    _notify_system_admins(
        db,
        message=f"{email} applied to be Institution Admin for {institution.name}",
        link="/admin/users",
    )
    log_audit(
        db, actor_user_id=user.id, action="institution_admin_applied",
        entity_type="user", entity_id=user.id, details=f"institution_id={institution_id}",
    )
    return user


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    if payload.role == UserRole.SYSTEM_ADMIN:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="System Admin accounts cannot be created through registration.")

    if payload.role == UserRole.REVIEWER:
        payload.role = UserRole.RESEARCHER

    if payload.role == UserRole.INSTITUTION_ADMIN:
        if payload.institution_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Select an institution to apply to.")
        return _create_institution_admin_application(
            db, payload.email, payload.institution_id, hash_password(payload.password), None, pre_verified=False
        )

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=UserRole.RESEARCHER,
        is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    db.add(Researcher(user_id=user.id))
    db.commit()

    _send_verification_email(db, user)
    log_audit(db, actor_user_id=user.id, action="user_registered", entity_type="user", entity_id=user.id)

    return user


@router.post("/verify-email")
def verify_email(payload: VerifyEmailRequest, db: Session = Depends(get_db)) -> dict:
    record = db.query(AuthToken).filter(AuthToken.token == payload.token).first()
    if record is None or record.token_type != AuthTokenType.EMAIL_VERIFICATION or not record.is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification link")

    user = db.query(User).filter(User.id == record.user_id).first()
    user.is_verified = True
    record.used_at = datetime.utcnow()
    db.commit()

    log_audit(db, actor_user_id=user.id, action="email_verified", entity_type="user", entity_id=user.id)
    return {"message": "Email verified. You can now log in."}


@router.post("/resend-verification")
def resend_verification(payload: ResendVerificationRequest, db: Session = Depends(get_db)) -> dict:
    user = db.query(User).filter(User.email == payload.email).first()
    if user is not None and not user.is_verified:
        _send_verification_email(db, user)
    return {"message": "If that account exists and isn't verified yet, a new link has been sent."}


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> dict:
    fifteen_min_ago = datetime.utcnow() - timedelta(minutes=15)
    recent_failures = (
        db.query(AuditLog)
        .filter(
            AuditLog.action == "login_failed",
            AuditLog.details == form_data.username,
            AuditLog.created_at >= fifteen_min_ago,
        )
        .count()
    )
    if recent_failures >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Please try again in 15 minutes.",
        )

    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not user.password_hash or not verify_password(form_data.password, user.password_hash):
        log_audit(db, actor_user_id=user.id if user else None, action="login_failed", entity_type="user", details=form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This account is inactive or awaiting approval.")

    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Please verify your email before logging in.")

    if user.mfa_enabled:
        _send_mfa_otp_email(db, user)
        pre_auth_token = create_access_token(subject=user.email, expires_minutes=10)
        return {"access_token": "", "token_type": "bearer", "mfa_required": True, "pre_auth_token": pre_auth_token}

    access_token = create_access_token(subject=user.email)
    log_audit(db, actor_user_id=user.id, action="user_login", entity_type="user", entity_id=user.id)
    return {"access_token": access_token, "token_type": "bearer", "mfa_required": False}


@router.post("/mfa/verify-login", response_model=Token)
def verify_mfa_login(pre_auth_token: str = Body(...), code: str = Body(...), db: Session = Depends(get_db)) -> dict:
    email = decode_access_token(pre_auth_token)
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired, please log in again")
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.mfa_enabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MFA is not enabled for this account")

    otp_record = (
        db.query(AuthToken)
        .filter(AuthToken.user_id == user.id, AuthToken.token_type == AuthTokenType.MFA_OTP, AuthToken.token == code)
        .order_by(AuthToken.created_at.desc())
        .first()
    )
    if not otp_record or not otp_record.is_valid:
        log_audit(db, actor_user_id=user.id, action="mfa_failed", entity_type="user", entity_id=user.id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired code")

    otp_record.used_at = datetime.utcnow()
    access_token = create_access_token(subject=user.email)
    log_audit(db, actor_user_id=user.id, action="user_login", entity_type="user", entity_id=user.id, details="mfa")
    db.commit()
    return {"access_token": access_token, "token_type": "bearer", "mfa_required": False}


@router.post("/mfa/resend-otp")
def resend_mfa_otp(pre_auth_token: str = Body(..., embed=True), db: Session = Depends(get_db)) -> dict:
    email = decode_access_token(pre_auth_token)
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired, please log in again")
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.mfa_enabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MFA is not enabled for this account")

    _send_mfa_otp_email(db, user)
    return {"sent": True}


@router.post("/mfa/enable")
def enable_mfa(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    current_user.mfa_enabled = True
    db.commit()
    log_audit(db, actor_user_id=current_user.id, action="mfa_enabled", entity_type="user", entity_id=current_user.id)
    return {"mfa_enabled": True}


@router.post("/mfa/disable")
def disable_mfa(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    current_user.mfa_enabled = False
    db.commit()
    log_audit(db, actor_user_id=current_user.id, action="mfa_disabled", entity_type="user", entity_id=current_user.id)
    return {"mfa_enabled": False}


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user

    
@router.post("/google", response_model=GoogleSignInResult)
def google_sign_in(payload: GoogleSignInRequest, db: Session = Depends(get_db)) -> GoogleSignInResult:
    try:
        decoded = google_id_token.verify_oauth2_token(
            payload.id_token, google_requests.Request(), settings.GOOGLE_CLIENT_ID
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid Google sign-in token: {e}")

    google_sub = decoded["sub"]
    email = decoded["email"]

    user = db.query(User).filter(User.google_sub == google_sub).first()
    if user is None:
        user = db.query(User).filter(User.email == email).first()

    if user is not None:
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This account is inactive or awaiting approval.")
        if user.google_sub is None:
            user.google_sub = google_sub
            db.commit()
        access_token = create_access_token(subject=user.email)
        log_audit(db, actor_user_id=user.id, action="user_login_google", entity_type="user", entity_id=user.id)
        return GoogleSignInResult(access_token=access_token)

    if payload.role is None:
        return GoogleSignInResult(needs_role_selection=True, email=email)

    if payload.role == UserRole.SYSTEM_ADMIN:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="System Admin accounts cannot be created through registration.")

    if payload.role == UserRole.REVIEWER:
        payload.role = UserRole.RESEARCHER

    if payload.role == UserRole.INSTITUTION_ADMIN:
        if payload.institution_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Select an institution to apply to.")
        _create_institution_admin_application(db, email, payload.institution_id, None, google_sub, pre_verified=True)
        return GoogleSignInResult(
            pending_approval=True,
            message="Your Institution Admin application has been submitted and is awaiting approval.",
            email=email,
        )

    user = User(email=email, password_hash=None, google_sub=google_sub, role=UserRole.RESEARCHER, is_verified=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    db.add(Researcher(user_id=user.id))
    db.commit()

    log_audit(db, actor_user_id=user.id, action="user_registered_google", entity_type="user", entity_id=user.id)

    access_token = create_access_token(subject=user.email)
    return GoogleSignInResult(access_token=access_token)


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)) -> dict:
    user = db.query(User).filter(User.email == payload.email).first()
    if user is not None and user.password_hash is not None:
        token = AuthToken.generate(user.id, AuthTokenType.PASSWORD_RESET, hours_valid=2)
        db.add(token)
        db.commit()

        link = f"{settings.FRONTEND_URL}/reset-password?token={token.token}"
        send_email(
            to_email=user.email,
            subject="Reset your SCNA password",
            html_body=render_email(
                title="Reset your password",
                body_html="<p>We received a request to reset your password. If this wasn't you, you can safely ignore this email.</p><p>This link is valid for 2 hours.</p>",
                cta_text="Reset Password",
                cta_link=link,
            ),
        )
        log_audit(db, actor_user_id=user.id, action="password_reset_requested", entity_type="user", entity_id=user.id)

    return {"message": "If that email is registered with a password, a reset link has been sent."}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)) -> dict:
    record = db.query(AuthToken).filter(AuthToken.token == payload.token).first()
    if record is None or record.token_type != AuthTokenType.PASSWORD_RESET or not record.is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset link")

    user = db.query(User).filter(User.id == record.user_id).first()
    user.password_hash = hash_password(payload.new_password)
    record.used_at = datetime.utcnow()
    db.commit()

    log_audit(db, actor_user_id=user.id, action="password_reset_completed", entity_type="user", entity_id=user.id)
    return {"message": "Password updated. You can now log in with your new password."}