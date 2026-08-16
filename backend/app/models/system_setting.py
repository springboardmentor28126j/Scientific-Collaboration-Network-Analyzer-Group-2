from datetime import datetime

from sqlalchemy import String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SystemSetting(Base):
    """
    Simple key/value store for platform-wide configuration that System Admins
    can change without a code deploy (e.g. registration toggles, review
    deadlines). Deliberately schemaless -- new keys don't need a migration.
    """
    __tablename__ = "system_setting"

    setting_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    updated_by: Mapped[int | None] = mapped_column(ForeignKey("user.user_id", ondelete="SET NULL"), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    updated_by_user: Mapped["User"] = relationship()
