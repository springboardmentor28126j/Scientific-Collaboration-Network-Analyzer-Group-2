from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.audit import log_audit
from app.core.captcha import verify_recaptcha
from app.core.config import settings
from app.core.email import send_email
from app.core.security import create_access_token, decode_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.auth_token import AuthToken, AuthTokenType
from app.models.researcher import Researcher
from app.models.user import User, UserRole
from app.schemas.auth import ForgotPasswordRequest, MfaResendRequest, MfaVerifyRequest, ResetPasswordRequest
from app.api.deps import get_current_user
from app.schemas.user import Token, UserCreate, UserOut

router = APIRouter()


def _send_mfa_otp_email(db: Session, user: User, background_tasks: BackgroundTasks) -> AuthToken:
    """Generates + persists a 6-digit OTP for user and emails it. Callers
    are responsible for committing (this only adds+commits the token row
    itself, matching the pattern already used by forgot_password() below
    for password-reset tokens)."""
    otp = AuthToken.generate_otp(user.id)
    db.add(otp)
    db.commit()
    background_tasks.add_task(
        send_email,
        to_email=user.email,
        subject="Your SCNA login code",
        body=(
            f"Your one-time login code is: {otp.token}\n\n"
            "This code expires in 10 minutes. If you didn't try to log in, "
            "you can ignore this email."
        ),
    )
    return otp


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Self-registration only ever creates a Researcher account. Institution
    # Admin / Reviewer / System Admin accounts are granted by an existing
    # admin (see the admin user-management endpoints), never chosen by the
    # person signing up — the role on the incoming payload is ignored.
    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=UserRole.RESEARCHER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Every self-registered user gets an (initially empty) researcher profile
    # row so /researchers/me works immediately after signup.
    db.add(Researcher(user_id=user.id))
    db.commit()

    log_audit(
        db,
        user_id=user.id,
        action="register",
        entity_type="user",
        entity_id=user.id,
        details=f"email={user.email}",
    )
    return user


@router.post("/login", response_model=Token)
def login(
    background_tasks: BackgroundTasks,
    form_data: OAuth2PasswordRequestForm = Depends(),
    g_recaptcha_response: str = Form(default=""),
    db: Session = Depends(get_db),
) -> dict:
    if not verify_recaptcha(g_recaptcha_response):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Captcha verification failed. Please try again.",
        )

    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        log_audit(
            db,
            user_id=user.id if user else None,
            action="login_failed",
            entity_type="user",
            entity_id=user.id if user else None,
            details=f"email={form_data.username}",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.mfa_enabled:
        _send_mfa_otp_email(db, user, background_tasks)
        pre_auth_token = create_access_token(subject=user.email, expires_minutes=10)
        return {"access_token": "", "token_type": "bearer", "mfa_required": True, "pre_auth_token": pre_auth_token}

    access_token = create_access_token(subject=user.email)
    log_audit(
        db, user_id=user.id, action="login", entity_type="user", entity_id=user.id
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/mfa/verify-login", response_model=Token)
def verify_mfa_login(payload: MfaVerifyRequest, db: Session = Depends(get_db)) -> dict:
    email = decode_access_token(payload.pre_auth_token)
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired, please log in again")
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.mfa_enabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MFA is not enabled for this account")

    otp_record = (
        db.query(AuthToken)
        .filter(AuthToken.user_id == user.id, AuthToken.token_type == AuthTokenType.MFA_OTP, AuthToken.token == payload.code)
        .order_by(AuthToken.created_at.desc())
        .first()
    )
    if not otp_record or not otp_record.is_valid:
        log_audit(db, user_id=user.id, action="mfa_failed", entity_type="user", entity_id=user.id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired code")

    otp_record.used_at = datetime.utcnow()
    access_token = create_access_token(subject=user.email)
    log_audit(db, user_id=user.id, action="login", entity_type="user", entity_id=user.id, details="mfa")
    db.commit()
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/mfa/resend-otp")
def resend_mfa_otp(
    payload: MfaResendRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
) -> dict:
    email = decode_access_token(payload.pre_auth_token)
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired, please log in again")
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.mfa_enabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MFA is not enabled for this account")

    _send_mfa_otp_email(db, user, background_tasks)
    return {"sent": True}


@router.post("/mfa/enable")
def enable_mfa(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    current_user.mfa_enabled = True
    db.commit()
    log_audit(db, user_id=current_user.id, action="mfa_enabled", entity_type="user", entity_id=current_user.id)
    return {"mfa_enabled": True}


@router.post("/mfa/disable")
def disable_mfa(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    current_user.mfa_enabled = False
    db.commit()
    log_audit(db, user_id=current_user.id, action="mfa_disabled", entity_type="user", entity_id=current_user.id)
    return {"mfa_enabled": False}


@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.post("/forgot-password")
def forgot_password(
    payload: ForgotPasswordRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
) -> dict:
    # Always return the same generic message whether or not the account
    # exists, so this endpoint can't be used to enumerate registered
    # emails. The actual token + email only get generated for a real,
    # password-based account.
    user = db.query(User).filter(User.email == payload.email).first()
    if user is not None and user.password_hash is not None:
        token = AuthToken.generate(user.id, AuthTokenType.PASSWORD_RESET, hours_valid=2)
        db.add(token)
        db.commit()

        link = f"{settings.FRONTEND_URL}/reset-password?token={token.token}"
        background_tasks.add_task(
            send_email,
            to_email=user.email,
            subject="Reset your SCNA password",
            body=(
                "We received a request to reset your password. If this wasn't you, "
                "you can safely ignore this email.\n\n"
                f"Reset your password: {link}\n\n"
                "This link is valid for 2 hours."
            ),
        )
        log_audit(
            db,
            user_id=user.id,
            action="password_reset_requested",
            entity_type="user",
            entity_id=user.id,
        )

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

    log_audit(
        db,
        user_id=user.id,
        action="password_reset_completed",
        entity_type="user",
        entity_id=user.id,
    )
    return {"message": "Password updated. You can now log in with your new password."}
