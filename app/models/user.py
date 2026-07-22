import enum
from datetime import datetime

from sqlalchemy import String, DateTime, func, ForeignKey, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserRole(str, enum.Enum):
    RESEARCHER = "researcher"
    INSTITUTION_ADMIN = "institution_admin"
    REVIEWER = "reviewer"
    SYSTEM_ADMIN = "system_admin"


class AuthProvider(str, enum.Enum):
    LOCAL = "local"
    GOOGLE = "google"


class User(Base):
    __tablename__ = "user"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)

    # Nullable because Google-only accounts have no local password.
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)

    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    institution_id: Mapped[int | None] = mapped_column(
        ForeignKey("institution.institution_id", ondelete="SET NULL"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_email_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )

    auth_provider: Mapped[AuthProvider] = mapped_column(
        Enum(AuthProvider), default=AuthProvider.LOCAL, nullable=False
    )
    google_sub: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    institution: Mapped["Institution"] = relationship(back_populates="users")
    researcher_profile: Mapped["ResearcherProfile"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )