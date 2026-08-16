import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core import redis_client
from app.core.config import settings
from app.core.email_sender import send_verification_email, send_password_reset_email, send_password_reset_unavailable_email
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.models.user import User, UserRole, AffiliationStatus, AuthProvider
from app.models.institution import Institution
from app.models.institution_request import InstitutionRequest
from app.repositories import user_repository, email_verification_repository, password_reset_repository
from app.utils.audit import write_audit_log
from app.utils.notifications import notify
from jose import JWTError
from sqlalchemy import select, func


def _match_institution_by_email_domain(db: Session, email: str) -> Institution | None:
    email_domain = email.split("@")[-1].lower()
    return db.scalar(
        select(Institution).where(Institution.email_domain.isnot(None), func.lower(Institution.email_domain) == email_domain)
    )


def _resolve_member_institution(
    db: Session, email: str, role: UserRole, institution_id: int | None
) -> tuple[int | None, AffiliationStatus]:
    """
    Shared institution-affiliation resolution for RESEARCHER and REVIEWER
    accounts. Both of these can be either "institutional" (institution_id
    set) or "independent" (institution_id left blank) -- unlike Institution
    Admins, they never require System Admin approval to register, only
    (optionally) their own institution's admin sign-off on the affiliation.

    - No institution selected: auto-detect via email domain match (BR:
      "abc@annauniv.edu -> auto-detect Institution = Anna University"); if
      nothing matches, they're an independent researcher/reviewer.
    - Institution selected AND it has a configured email_domain: the
      account's email must match that domain. BR: "Institutional
      researcher/reviewer are accepted only if they are registering with
      their institution's official email id; if they try to register with
      a personal email id they are not allowed to register under the
      institution." A mismatch is a hard rejection, not a pending queue --
      the person must either use their official email or register without
      selecting an institution (as independent).
    - Institution selected but it has no email_domain on file (nothing to
      verify automatically against): falls back to the institution admin's
      manual approval queue (PENDING), same as before.
    """
    detected = _match_institution_by_email_domain(db, email)

    if institution_id is None:
        if detected is not None:
            return detected.institution_id, AffiliationStatus.APPROVED
        return None, AffiliationStatus.NOT_APPLICABLE

    institution = db.get(Institution, institution_id)
    if institution is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Selected institution does not exist.")

    if institution.email_domain:
        email_domain = email.split("@")[-1].lower()
        if email_domain != institution.email_domain.lower():
            role_label = role.value.replace("_", " ").title()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Institutional {role_label} accounts for {institution.name} must register with an "
                    f"@{institution.email_domain} email address. A personal email address cannot be "
                    "registered under an institution -- leave the institution field blank to register "
                    f"as an independent {role_label.lower()} instead."
                ),
            )
        return institution_id, AffiliationStatus.APPROVED

    if detected is not None and detected.institution_id == institution_id:
        return institution_id, AffiliationStatus.APPROVED

    # Institution has no domain on file, so there's nothing to auto-verify
    # against -- queue for the institution admin's manual review instead of
    # silently trusting the claimed affiliation.
    return institution_id, AffiliationStatus.PENDING


def _enforce_email_domain_policy(db: Session, email: str, role: UserRole, institution_id: int) -> Institution:
    """
    Used for Institution Admin applications against an *existing*
    institution: their email must match that institution's configured
    domain, if one is configured. Returns the institution row so callers
    don't have to re-fetch it. institution_id is required (non-None) here --
    callers must already have handled the "no institution selected" case.
    """
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
    return institution


def _notify_institution_admins_of_pending_affiliation(db: Session, user: User) -> None:
    if user.affiliation_status != AffiliationStatus.PENDING or user.institution_id is None:
        return
    admin_ids = db.scalars(
        select(User.user_id).where(
            User.institution_id == user.institution_id, User.role == UserRole.INSTITUTION_ADMIN
        )
    ).all()
    for admin_id in admin_ids:
        notify(
            db, admin_id, "affiliation_pending", "New researcher affiliation request",
            f"{user.email} has requested to join your institution and is awaiting approval.",
            link_url="/institution-admin/researchers?affiliation_status=pending",
        )


def _notify_system_admins_of_pending_institution_admin(db: Session, user: User, institution_label: str) -> None:
    admin_ids = db.scalars(select(User.user_id).where(User.role == UserRole.SYSTEM_ADMIN)).all()
    for admin_id in admin_ids:
        notify(
            db, admin_id, "institution_admin_pending", "New Institution Admin application",
            f"{user.email} has applied to be Institution Admin for {institution_label} and is awaiting approval.",
            link_url="/admin/users?role=institution_admin&affiliation_status=pending",
        )


def set_researcher_institution(db: Session, user: User, institution_id: int) -> User:
    """
    Self-service institution linking for an existing Researcher whose
    account has no institution on file -- most commonly because their
    institution's email_domain wasn't configured yet at the time they
    signed up, so the automatic match in _resolve_member_institution had
    nothing to match against.

    Reuses that same function so the rules stay identical to registration:
    if the chosen institution's email domain matches this account's email,
    the affiliation is approved immediately; if the institution has no
    domain configured (or a different one), it's queued as PENDING for
    that institution's admin to approve, same as at signup.
    """
    if user.role != UserRole.RESEARCHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only researcher accounts can set their institution this way.",
        )

    resolved_institution_id, affiliation_status = _resolve_member_institution(
        db, user.email, user.role, institution_id
    )

    user.institution_id = resolved_institution_id
    user.affiliation_status = affiliation_status
    db.commit()
    db.refresh(user)

    write_audit_log(db, user.user_id, "UPDATE", "user", user.user_id, "Self-service institution affiliation")
    _notify_institution_admins_of_pending_affiliation(db, user)
    return user


def register_user(
    db: Session,
    email: str,
    password: str,
    role: UserRole,
    institution_id: int | None,
    institution_name: str | None = None,
    website: str | None = None,
    domain: str | None = None,
    address: str | None = None,
    official_email: str | None = None,
) -> User:
    if user_repository.get_by_email(db, email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    if role == UserRole.SYSTEM_ADMIN:
        # BR: "System Admin can be created by inserting directly into
        # PostgreSQL." There is no self-service path to this role -- it must
        # never be reachable through public registration (local or Google).
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="System Admin accounts cannot be created through registration.",
        )

    if role == UserRole.INSTITUTION_ADMIN:
        # BR (both branches): becoming an Institution Admin always requires
        # System Admin approval before the account is activated --
        # "Apply as Institution Admin -> System Admin Approval -> Institution
        # Admin Activated" -- whether the institution already exists or is
        # being requested fresh. The account is created inactive
        # (is_active=False) so it cannot log in until a System Admin approves
        # it via /users/{id}/approve-affiliation (existing institution) or
        # /institutions/requests/{id}/approve (new institution).
        if institution_id is not None:
            institution = _enforce_email_domain_policy(db, email, role, institution_id)
            user = user_repository.create_user(
                db, email=email, password_hash=hash_password(password), role=role, institution_id=institution_id,
                affiliation_status=AffiliationStatus.PENDING, is_active=False,
            )
            write_audit_log(db, user_id=user.user_id, action="CREATE", entity_type="user", entity_id=user.user_id)
            _notify_system_admins_of_pending_institution_admin(db, user, institution.name)
            send_new_verification_email(db, user)
            return user
        else:
            if not institution_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Provide institution details to request a new institution.",
                )
            user = user_repository.create_user(
                db, email=email, password_hash=hash_password(password), role=role, institution_id=None,
                affiliation_status=AffiliationStatus.PENDING, is_active=False,
            )
            request_row = InstitutionRequest(
                institution_name=institution_name,
                website=website,
                domain=domain,
                address=address,
                official_email=official_email,
                status="PENDING",
                requested_by_user_id=user.user_id,
            )
            db.add(request_row)
            write_audit_log(db, user_id=user.user_id, action="CREATE", entity_type="user", entity_id=user.user_id)
            _notify_system_admins_of_pending_institution_admin(db, user, institution_name)
            send_new_verification_email(db, user)
            return user

    # RESEARCHER and REVIEWER: both support "institutional" (institution_id
    # set) and "independent" (institution_id left blank) variants, and never
    # require System Admin approval just to register.
    institution_id, affiliation_status = _resolve_member_institution(db, email, role, institution_id)

    user = user_repository.create_user(
        db, email=email, password_hash=hash_password(password), role=role, institution_id=institution_id,
        affiliation_status=affiliation_status,
    )
    write_audit_log(db, user_id=user.user_id, action="CREATE", entity_type="user", entity_id=user.user_id)
    _notify_institution_admins_of_pending_affiliation(db, user)

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
    if user is None or user.is_email_verified or user.auth_provider != AuthProvider.LOCAL:
        return
    send_new_verification_email(db, user)


def request_password_reset(db: Session, email: str) -> None:
    """
    Always returns None regardless of outcome -- callers (the API endpoint)
    give the same response whether or not the email is registered, to avoid
    leaking which emails have accounts. What actually happens:

    - No account with this email: nothing happens.
    - Google-only account (no local password): no reset link is issued
      (there'd be nothing to reset), but we email the account owner to
      explain they should use "Sign in with Google" instead -- that's safe
      to tell the account owner even though the API response stays generic.
    - Local account: a fresh single-use reset link is emailed, and any
      previously-issued unused reset link for this user is invalidated.
    """
    user = user_repository.get_by_email(db, email)
    if user is None:
        return

    if user.auth_provider != AuthProvider.LOCAL:
        send_password_reset_unavailable_email(user.email)
        return

    password_reset_repository.invalidate_existing_tokens_for_user(db, user.user_id)

    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
    password_reset_repository.create_token(db, user_id=user.user_id, token=token, expires_at=expires_at)

    reset_link = f"{settings.FRONTEND_BASE_URL}/reset-password?token={token}"
    send_password_reset_email(user.email, reset_link)


def reset_password(db: Session, token: str, new_password: str) -> None:
    record = password_reset_repository.get_by_token(db, token)
    if record is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired password reset link")
    if record.used:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This password reset link was already used")
    if password_reset_repository.is_expired(record):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This password reset link has expired. Please request a new one.",
        )

    user = user_repository.get_by_id(db, record.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.auth_provider != AuthProvider.LOCAL:
        # issued), but guard against a stale token from before an account
        # was linked to Google.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account signs in with Google and doesn't have a password to reset.",
        )

    user.password_hash = hash_password(new_password)
    db.commit()

    password_reset_repository.mark_used(db, record)
    # Belt-and-braces: invalidate any other outstanding reset links for this
    # user too, in case more than one was requested before this one was used.
    password_reset_repository.invalidate_existing_tokens_for_user(db, user.user_id)

    # A changed password should immediately invalidate every existing
    # session -- otherwise a stolen refresh token would keep working even
    # after the account owner "secured" it with a new password.
    redis_client.revoke_all_sessions_for_user(user.user_id)

    write_audit_log(db, user_id=user.user_id, action="UPDATE", entity_type="user", entity_id=user.user_id, details="Password reset")
    notify(
        db, user.user_id, "password_reset", "Password changed",
        "Your password was just reset. If this wasn't you, contact support immediately.",
        link_url="/profile",
    )


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = user_repository.get_by_email(db, email)
    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if not user.is_active:
        if user.role == UserRole.INSTITUTION_ADMIN and user.affiliation_status == AffiliationStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your Institution Admin application is awaiting System Admin approval.",
            )
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
    try:
        decoded = google_id_token.verify_oauth2_token(token, google_requests.Request(), settings.GOOGLE_CLIENT_ID)
    except Exception as exc:
        raise ValueError("Invalid Google ID token") from exc

    google_sub = decoded["sub"]
    email = decoded["email"]

    user = db.query(User).filter(User.google_sub == google_sub).first()
    if user is None:
        user = user_repository.get_by_email(db, email)

    if user is not None:
        # Existing account -- either already Google-linked, or a local
        # account signing in with Google for the first time (link it now).
        # Same activation check local login enforces (authenticate_user) --
        # without it, a deactivated user or a not-yet-approved pending
        # Institution Admin application could sign in via Google and get
        # valid tokens despite is_active=False.
        if not user.is_active:
            raise ValueError(
                "Account is deactivated or awaiting approval. "
                "Contact your institution admin or platform support if this is unexpected."
            )
        if user.auth_provider != AuthProvider.GOOGLE:
            user.auth_provider = AuthProvider.GOOGLE
            user.google_sub = google_sub
            user.is_email_verified = True
            db.commit()
        write_audit_log(db, user_id=user.user_id, action="LOGIN", entity_type="user", entity_id=user.user_id)
        return issue_tokens(user)

    if role is None:
        # Brand-new account, no role chosen yet.
        return None

    if role == UserRole.SYSTEM_ADMIN:
        raise ValueError("System Admin accounts cannot be created through registration.")

    if role == UserRole.INSTITUTION_ADMIN:
        # Same approval requirement as local registration -- Google sign-in
        # only supports applying to an *existing* institution (there's no
        # "request a new institution" form in that flow), and it still
        # requires System Admin approval before activation.
        if institution_id is None:
            raise ValueError("Institution Admin accounts must select an institution.")
        institution = _enforce_email_domain_policy(db, email, role, institution_id)
        user = user_repository.create_user(
            db, email=email, password_hash=None, role=role, institution_id=institution_id,
            affiliation_status=AffiliationStatus.PENDING, is_active=False,
        )
        user.auth_provider = AuthProvider.GOOGLE
        user.google_sub = google_sub
        user.is_email_verified = True
        db.commit()
        db.refresh(user)
        write_audit_log(db, user_id=user.user_id, action="CREATE", entity_type="user", entity_id=user.user_id)
        _notify_system_admins_of_pending_institution_admin(db, user, institution.name)
        # Don't issue tokens and don't return None (that value is reserved
        # for "brand-new account, still need a role" and would make the
        # frontend re-prompt for role selection). Raise instead so the
        # caller surfaces a clear pending-approval message.
        raise ValueError(
            "Your Institution Admin application has been submitted and is awaiting System Admin approval. "
            "You'll be notified once it's reviewed."
        )

    institution_id, affiliation_status = _resolve_member_institution(db, email, role, institution_id)

    user = user_repository.create_user(
        db, email=email, password_hash=None, role=role, institution_id=institution_id,
        affiliation_status=affiliation_status,
    )
    user.auth_provider = AuthProvider.GOOGLE
    user.google_sub = google_sub
    user.is_email_verified = True
    db.commit()
    db.refresh(user)

    write_audit_log(db, user_id=user.user_id, action="CREATE", entity_type="user", entity_id=user.user_id)
    _notify_institution_admins_of_pending_affiliation(db, user)
    return issue_tokens(user)