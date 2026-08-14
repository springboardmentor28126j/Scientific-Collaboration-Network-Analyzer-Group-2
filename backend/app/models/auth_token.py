import enum
import secrets
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, utcnow


class AuthTokenType(str, enum.Enum):
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"
    MFA_OTP = "mfa_otp"


class AuthToken(Base):
    """A single-use, expiring token used for the password-reset link
    (and, unused for now but kept for future reuse, email verification).
    Rows are inserted by POST /auth/forgot-password and consumed by
    POST /auth/reset-password -- see app/api/routes/auth.py.
    """

    __tablename__ = "auth_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    token_type: Mapped[AuthTokenType] = mapped_column(
        Enum(AuthTokenType, values_callable=lambda enum_cls: [m.value for m in enum_cls]),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    user: Mapped["User"] = relationship("User")

    @staticmethod
    def generate(user_id: int, token_type: "AuthTokenType", hours_valid: int = 24) -> "AuthToken":
        return AuthToken(
            user_id=user_id,
            token=secrets.token_urlsafe(32),
            token_type=token_type,
            expires_at=utcnow() + timedelta(hours=hours_valid),
        )

    @staticmethod
    def generate_otp(user_id: int, minutes_valid: int = 10) -> "AuthToken":
        """A short numeric code (not a URL-safe token) meant to be typed in
        by hand from an email, not clicked as a link -- see generate()
        above for the link-style tokens used by password reset / email
        verification."""
        code = f"{secrets.randbelow(1_000_000):06d}"
        return AuthToken(
            user_id=user_id,
            token=code,
            token_type=AuthTokenType.MFA_OTP,
            expires_at=utcnow() + timedelta(minutes=minutes_valid),
        )

    @property
    def is_valid(self) -> bool:
        return self.used_at is None and self.expires_at > utcnow()
