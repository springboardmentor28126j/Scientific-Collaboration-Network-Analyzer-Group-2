import uuid
import enum

from sqlalchemy import (
    UniqueConstraint,
    CheckConstraint,
    String,
    Boolean,
    Enum,
    DateTime,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base_model import TimestampMixin
from app.db.database import Base
from app.db.database import Base
from datetime import datetime

class UserRole(str, enum.Enum):
    RESEARCHER = "Researcher"
    REVIEWER = "Reviewer"
    INSTITUTION_ADMIN = "InstitutionAdmin"
    SYSTEM_ADMIN = "SystemAdmin"


class User(TimestampMixin,Base):
    __tablename__ = "users"
    __table_args__ = (
	UniqueConstraint("email",name="uq_user_email"),
)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    email = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = mapped_column(
        String(255),
        nullable=False
    )

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.RESEARCHER,
        nullable=False
    )

    is_active = mapped_column(
        Boolean,
        default=False,
	nullable=False
    )
    email_verified = mapped_column(
    	Boolean,
    	default=False,
    	nullable=False,
    )

    verification_token = mapped_column(
    	String(255),
    	nullable=True,
    )

    verification_token_expiry = mapped_column(
    	DateTime,
    	nullable=True,
    )

    password_reset_token = mapped_column(
    	String(255),
    	nullable=True,
    )

    password_reset_expiry = mapped_column(
    	DateTime,
    	nullable=True,
    )

    researcher = relationship(
        "Researcher",
        back_populates="user",
	cascade="all, delete-orphan",
        uselist=False
    )
    publications = relationship(
    	"Publication",
    	back_populates="owner",
	cascade="all, delete-orphan"
    )

    conference_registrations = relationship(
        "ConferenceRegistration",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
    )
