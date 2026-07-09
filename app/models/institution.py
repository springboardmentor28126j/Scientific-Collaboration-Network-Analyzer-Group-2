from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User


class Institution(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    A registered institution (university, lab, research body, etc).

    is_active here is the *platform-level* kill switch — only the
    superuser can flip it. When False, every user belonging to this
    institution is instantly locked out, regardless of their own
    is_active flag (enforced in the auth dependency, not at the DB level).
    """

    __tablename__ = "institutions"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    logo_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    logo_public_id: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    users: Mapped[list["User"]] = relationship(
        "User", back_populates="institution", cascade="all, delete-orphan"
    )
