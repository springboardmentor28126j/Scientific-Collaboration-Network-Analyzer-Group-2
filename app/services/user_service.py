import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core import redis_client
from app.core.config import settings
from app.core.email_sender import send_verification_email
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.models.user import User, UserRole
from app.models.institution import Institution
from app.repositories import user_repository, email_verification_repository
from app.utils.audit import write_audit_log
from jose import JWTError


def _enforce_email_domain_policy(db: Session, email: str, role: UserRole, institution_id: int | None) -> None:
    """
    Researchers can register with any email (personal Gmail, etc).
    Institution admins and reviewers must belong to a specific institution,
    and if that institution has an email_domain configured, their email must
    match it -- e.g. an institution_admin for "SRM College" (email_domain
    "srm.edu.in") can't register with a personal gmail.com address.
    If the institution hasn't configured an email_domain yet, the domain
    check is skipped so onboarding isn't blocked on that being set up first.
    """
    if role == UserRole.RESEARCHER:
        return

    if institution_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{role.value.replace('_', ' ').title()} accounts must select an institution.",
        )

    institution = db.get(Institution, institution_id)
    if institution is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Selected institution does not exist.")

    if institution.email_domain:
        email_domain = email.split("@")[-1].lower()
        if email_domain != institution.email_domain.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"{role.value.replace('_', ' ').title()} accounts for {institution.name} "
                    f"must register with an @{institution.email_domain} email address."
                ),
            )


def register_user(db: Session, email: str, password: str, role: UserRole, institution_id: int | None) -> User:
    if user_repository.get_by_email(db, email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    _enforce_email_domain_policy(db, email, role, institution_id)

    user = user_repository.create_user(
        db, email=email, password_hash=hash_password(password), role=role, institution_id=institution_id
    )
    write_audit_log(db, user_id=user.user_id, action="CREATE", entity_type="user", entity_id=user.user_id)

    # Local (email/password) accounts are unverified until they click the
    # emailed link. Google accounts skip this entirely -- see google_sign_in.
    send_new_verification_email(db, user)
    return user


def send_new_verification_email(db: Session, user: User) -> None:
    email_verification_repository.invalidate_existing_tokens_for_user(db, user.user_id)

    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS)
    email_verification_repository.create_token(db, user_id=user.user_id, token=token, expires_at=expires_at)

    verification_link = f"{settings.FRONTEND_BASE_URL}/verify-email?token={token}"
    send_verification_email(user.email, verification_link)


def verify_email(db: Session, token: str) -> User:
    record = email_verification_repository.get_by_token(db, token)
    if record is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification link")
    if record.used:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This verification link was already used")
    if email_verification_repository.is_expired(record):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This verification link has expired. Please request a new one.",
        )

    user = user_repository.get_by_id(db, record.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_email_verified = True
    db.commit()
    email_verification_repository.mark_used(db, record)
    write_audit_log(db, user_id=user.user_id, action="UPDATE", entity_type="user", entity_id=user.user_id, details="Email verified")
    return user


def resend_verification_email(db: Session, email: str) -> None:
    user = user_repository.get_by_email(db, email)
    # Deliberately don't reveal whether the email exists -- same response
    # either way, to avoid leaking which emails are registered.
    if user is None or user.is_email_verified or user.auth_provider != "LOCAL":
        return
    send_new_verification_email(db, user)


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = user_repository.get_by_email(db, email)
    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")
    if not user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in. Check your inbox for the verification link.",
        )

    write_audit_log(db, user_id=user.user_id, action="LOGIN", entity_type="user", entity_id=user.user_id)
    return user


def issue_tokens(user: User) -> tuple[str, str]:
    """
    Issues a fresh access/refresh pair and registers both as active sessions
    in Redis. The Redis entry -- not just JWT signature validity -- is what
    `get_current_user` and `refresh_access_token` check going forward, which
    is what makes logout an actual revocation instead of a client-side no-op.
    """
    access = create_access_token(subject=str(user.user_id), role=user.role.value)
    refresh = create_refresh_token(subject=str(user.user_id))

    redis_client.create_access_session(access.jti, user.user_id, access.ttl_seconds)
    redis_client.create_refresh_session(refresh.jti, user.user_id, refresh.ttl_seconds)

    return access.token, refresh.token


def refresh_access_token(db: Session, refresh_token: str) -> tuple[str, str]:
    """
    Validates and rotates a refresh token: the presented refresh token must
    still have an active Redis session (i.e. not already used, not logged
    out). On success it is revoked and replaced with a brand new access +
    refresh pair, so a given refresh token can only ever be used once.
    """
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    jti = payload.get("jti")
    if jti is None or not redis_client.is_refresh_session_active(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked or already used. Please log in again.",
        )

    user = user_repository.get_by_id(db, int(payload["sub"]))
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    # Rotate: the old refresh token is single-use, so kill its session
    # before minting the replacement pair.
    redis_client.revoke_refresh_session(jti)
    return issue_tokens(user)


def logout_user(access_jti: str, refresh_token: str | None) -> None:
    """
    Revokes the current access session immediately and, if a refresh token
    was supplied, revokes that session too -- so both halves of the token
    pair stop working right away rather than lingering until natural expiry.
    """
    redis_client.revoke_access_session(access_jti)

    if refresh_token:
        try:
            payload = decode_token(refresh_token)
            refresh_jti = payload.get("jti")
            if refresh_jti:
                redis_client.revoke_refresh_session(refresh_jti)
        except JWTError:
            # Already invalid/expired -- nothing to revoke, and logout
            # should never fail just because the refresh token was stale.
            pass


from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests


def google_sign_in(
    db: Session, token: str, role: UserRole | None, institution_id: int | None
) -> tuple[str, str] | None:
    """
    Verifies a Google-issued id_token server-side (never trusts client-
    supplied identity directly), then either logs an existing account in,
    or -- for a brand-new Google account -- creates one, but only once a
    role has been supplied by the frontend's role-picker step.

    Returns None to signal "new account, still need a role" (auth.py's
    /auth/google endpoint turns that into needs_role_selection=True for
    the frontend), or an (access_token, refresh_token) pair on success.
    """
    decoded = google_id_token.verify_oauth2_token(token, google_requests.Request(), settings.GOOGLE_CLIENT_ID)
    google_sub = decoded["sub"]
    email = decoded["email"]

    user = db.query(User).filter(User.google_sub == google_sub).first()
    if user is None:
        user = user_repository.get_by_email(db, email)

    if user is not None:
        # Existing account -- either already Google-linked, or a local
        # account signing in with Google for the first time (link it now).
        if user.auth_provider != "GOOGLE":
            user.auth_provider = "GOOGLE"
            user.google_sub = google_sub
            user.is_email_verified = True
            db.commit()
        write_audit_log(db, user_id=user.user_id, action="LOGIN", entity_type="user", entity_id=user.user_id)
        return issue_tokens(user)

    if role is None:
        # Brand-new account, no role chosen yet.
        return None

    _enforce_email_domain_policy(db, email, role, institution_id)

    user = user_repository.create_user(
        db, email=email, password_hash=None, role=role, institution_id=institution_id
    )
    user.auth_provider = "GOOGLE"
    user.google_sub = google_sub
    user.is_email_verified = True
    db.commit()
    db.refresh(user)

    write_audit_log(db, user_id=user.user_id, action="CREATE", entity_type="user", entity_id=user.user_id)
    return issue_tokens(user)