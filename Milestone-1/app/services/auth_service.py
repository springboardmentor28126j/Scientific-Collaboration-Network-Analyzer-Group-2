"""
Business logic for authentication: login, token refresh, email/invite
verification, and forgot/reset password. Orchestrates the repositories —
routes in app/api/v1/auth.py stay thin and just call into this service.
"""

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ForbiddenError, InvalidTokenError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_raw_action_token,
    hash_action_token,
    hash_password,
    verify_action_token,
    verify_password,
)
from app.models.token import VerificationPurpose
from app.models.user import User
from app.repositories.token_repository import TokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenPair
from app.services.email_service import EmailService


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)
        self.tokens = TokenRepository(session)

    # --- Login / refresh ---

    async def authenticate(self, email: str, password: str) -> User:
        user = await self.users.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Incorrect email or password")

        if not user.is_verified:
            raise ForbiddenError("Account email has not been verified")
        if not user.is_active:
            raise ForbiddenError("Account has been deactivated")

        if user.institution is not None and not user.institution.is_active:
            raise ForbiddenError("Institution has been deactivated")

        return user

    def issue_token_pair(self, user: User) -> TokenPair:
        return TokenPair(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )

    async def refresh_access_token(self, refresh_token: str) -> TokenPair:
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid or expired refresh token")

        user = await self.users.get_by_id(uuid.UUID(payload["sub"]))
        if user is None or not user.is_active or not user.is_verified:
            raise UnauthorizedError("Account no longer active")
        if user.institution is not None and not user.institution.is_active:
            raise UnauthorizedError("Institution has been deactivated")

        return self.issue_token_pair(user)

    # --- Email / invite verification ---

    async def create_verification_token(
        self, user_id: uuid.UUID, purpose: VerificationPurpose
    ) -> str:
        """Generates a raw token, stores only its hash, returns the raw
        value so the caller can embed it in the emailed link."""
        raw_token = generate_raw_action_token()
        await self.tokens.create_verification_token(
            user_id=user_id,
            token_hash=hash_action_token(raw_token),
            purpose=purpose,
            expires_at=datetime.now(UTC) + timedelta(minutes=settings.EMAIL_TOKEN_EXPIRE_MINUTES),
        )
        return raw_token

    async def _resolve_verification_token(self, raw_token: str, purpose: VerificationPurpose):
        candidates = await self.tokens.get_active_verification_tokens(purpose)
        matched = next(
            (t for t in candidates if verify_action_token(raw_token, t.token_hash)), None
        )
        if matched is None:
            raise InvalidTokenError("This verification link is invalid or has expired")
        return matched

    async def verify_email_token(self, raw_token: str) -> User:
        """
        Institution admin email verification (EMAIL_VERIFY). The admin
        already set their password at self-registration time, so this
        step only needs to confirm the link and auto-activate the account
        (is_verified=True AND is_active=True in one step — see
        docs/architecture.md §5 for why these aren't separate gates).
        """
        matched = await self._resolve_verification_token(
            raw_token, VerificationPurpose.EMAIL_VERIFY
        )
        await self.tokens.mark_verification_token_used(matched)

        user = await self.users.get_by_id(matched.user_id)
        if user is None:
            raise InvalidTokenError("This verification link is invalid or has expired")

        return await self.users.set_verified_and_active(user)

    async def verify_invite_token(self, raw_token: str, new_password: str) -> User:
        """
        Researcher/Reviewer invite verification (INVITE_VERIFY). Unlike
        the institution admin, an invited user has no password yet — the
        institution admin only supplied email/name/description at
        creation time — so this step both sets the password and
        auto-activates the account in a single call.
        """
        matched = await self._resolve_verification_token(
            raw_token, VerificationPurpose.INVITE_VERIFY
        )
        await self.tokens.mark_verification_token_used(matched)

        user = await self.users.get_by_id(matched.user_id)
        if user is None:
            raise InvalidTokenError("This verification link is invalid or has expired")

        user = await self.users.set_password(user, hash_password(new_password))
        return await self.users.set_verified_and_active(user)

    # --- Forgot / reset password ---

    async def request_password_reset(self, email: str) -> None:
        """
        Always succeeds silently from the caller's point of view (no
        indication whether the email exists) to avoid user enumeration.
        Applies to any verified user — institution admin, researcher, or
        reviewer alike; unverified accounts have no password to reset yet,
        so they're naturally excluded by the is_verified check.
        """
        user = await self.users.get_by_email(email)
        if user is None or not user.is_verified:
            return

        raw_token = generate_raw_action_token()
        await self.tokens.create_reset_token(
            user_id=user.id,
            token_hash=hash_action_token(raw_token),
            expires_at=datetime.now(UTC)
            + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES),
        )
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={raw_token}"
        await EmailService.send_password_reset_email(user.email, user.full_name, reset_link)

    async def reset_password(self, raw_token: str, new_password: str) -> User:
        candidates = await self.tokens.get_active_reset_tokens()
        matched = next(
            (t for t in candidates if verify_action_token(raw_token, t.token_hash)), None
        )
        if matched is None:
            raise InvalidTokenError("This password reset link is invalid or has expired")

        await self.tokens.mark_reset_token_used(matched)

        user = await self.users.get_by_id(matched.user_id)
        if user is None:
            raise InvalidTokenError("This password reset link is invalid or has expired")

        return await self.users.set_password(user, hash_password(new_password))
