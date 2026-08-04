import uuid
import enum

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.base_model import TimestampMixin


class CollaborationStatus(str, enum.Enum):
    PENDING = "Pending"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"


class Collaboration(TimestampMixin, Base):
    __tablename__ = "collaborations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    sender_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "researchers.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    receiver_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "researchers.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    status: Mapped[CollaborationStatus] = mapped_column(
        Enum(CollaborationStatus),
        default=CollaborationStatus.PENDING,
        nullable=False,
    )

    sender = relationship(
        "Researcher",
        foreign_keys=[sender_id],
    )

    receiver = relationship(
        "Researcher",
        foreign_keys=[receiver_id],
    )