import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.token import EmailVerificationToken, PasswordResetToken, VerificationPurpose


class TokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # --- Email / invite verification tokens ---

    async def create_verification_token(
        self,
        user_id: uuid.UUID,
        token_hash: str,
        purpose: VerificationPurpose,
        expires_at: datetime,
    ) -> EmailVerificationToken:
        token = EmailVerificationToken(
            user_id=user_id, token_hash=token_hash, purpose=purpose, expires_at=expires_at
        )
        self.session.add(token)
        await self.session.flush()
        return token

    async def get_active_verification_tokens(
        self, purpose: VerificationPurpose
    ) -> list[EmailVerificationToken]:
        """All unused, unexpired tokens for a given purpose. The raw token
        from the emailed link isn't looked up by equality — only its hash
        is stored (bcrypt hashes aren't deterministic), so verification
        checks the raw token against each candidate's hash. Volumes here
        are small (one active token per pending user at a time), so the
        scan is cheap; revisit with an indexed lookup key if that changes."""
        result = await self.session.execute(
            select(EmailVerificationToken).where(
                EmailVerificationToken.purpose == purpose,
                EmailVerificationToken.used_at.is_(None),
                EmailVerificationToken.expires_at > datetime.now(UTC),
            )
        )
        return list(result.scalars().all())

    async def mark_verification_token_used(self, token: EmailVerificationToken) -> None:
        token.used_at = datetime.now(UTC)
        await self.session.flush()

    # --- Password reset tokens ---

    async def create_reset_token(
        self, user_id: uuid.UUID, token_hash: str, expires_at: datetime
    ) -> PasswordResetToken:
        token = PasswordResetToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
        self.session.add(token)
        await self.session.flush()
        return token

    async def get_active_reset_tokens(self) -> list[PasswordResetToken]:
        result = await self.session.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.used_at.is_(None),
                PasswordResetToken.expires_at > datetime.now(UTC),
            )
        )
        return list(result.scalars().all())

    async def mark_reset_token_used(self, token: PasswordResetToken) -> None:
        token.used_at = datetime.now(UTC)
        await self.session.flush()
