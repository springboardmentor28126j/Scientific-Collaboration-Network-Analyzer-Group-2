from datetime import datetime

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.audit import log_audit
from app.core.captcha import verify_recaptcha
from app.core.config import settings
from app.core.email import send_email
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.auth_token import AuthToken, AuthTokenType
from app.models.researcher import Researcher
from app.models.user import User, UserRole
from app.schemas.auth import ForgotPasswordRequest, ResetPasswordRequest
from app.schemas.user import Token, UserCreate, UserOut

router = APIRouter()


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

    access_token = create_access_token(subject=user.email)
    log_audit(
        db, user_id=user.id, action="login", entity_type="user", entity_id=user.id
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)) -> dict:
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
        send_email(
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
