from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, utcnow


class Institution(Base):
    __tablename__ = "institutions"

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Basic Information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    short_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    institution_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Contact Information
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Address Information
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Institution Status
    status: Mapped[str] = mapped_column(String(20), default="Active", nullable=False)

    # The Institution Admin who owns/manages this institution's record.
    # Nullable: institutions created before this column existed won't have
    # an admin on record until a System Admin assigns one.
    admin_user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )

    # Created Time
    created_at: Mapped[str] = mapped_column(
        DateTime,
        default=utcnow,
        nullable=False
    )

    # Relationship with Researcher
    researchers: Mapped[list["Researcher"]] = relationship(
        "Researcher",
        back_populates="institution"
    )