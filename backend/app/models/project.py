import enum
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Date, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, utcnow


class ProjectStatus(str, enum.Enum):
    PLANNED = "planned"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectMemberRole(str, enum.Enum):
    LEAD = "lead"
    MEMBER = "member"


class ProjectMemberStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, values_callable=lambda enum_cls: [m.value for m in enum_cls]),
        nullable=False,
        default=ProjectStatus.PLANNED,
        server_default="planned",
    )

    lead_researcher_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("researchers.id", ondelete="CASCADE"), nullable=False
    )
    institution_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("institutions.id", ondelete="SET NULL"), nullable=True
    )

    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    lead_researcher: Mapped["Researcher"] = relationship("Researcher", foreign_keys=[lead_researcher_id])
    institution: Mapped["Institution"] = relationship("Institution")
    members: Mapped[list["ProjectMember"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )

    @property
    def member_ids(self) -> list[int]:
        """Only ACCEPTED members. A pending invite isn't a member yet."""
        return [m.researcher_id for m in self.members if m.status == ProjectMemberStatus.ACCEPTED]


class ProjectMember(Base):
    """Collaborators on a project. The lead also gets a row here
    (role=LEAD, status=ACCEPTED) so 'who is on this project' is one query."""

    __tablename__ = "project_members"
    __table_args__ = (UniqueConstraint("project_id", "researcher_id", name="uq_project_member"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    researcher_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("researchers.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[ProjectMemberRole] = mapped_column(
        Enum(ProjectMemberRole, values_callable=lambda enum_cls: [m.value for m in enum_cls]),
        nullable=False,
        default=ProjectMemberRole.MEMBER,
        server_default="member",
    )
    status: Mapped[ProjectMemberStatus] = mapped_column(
        Enum(ProjectMemberStatus, values_callable=lambda enum_cls: [m.value for m in enum_cls]),
        nullable=False,
        server_default="pending",
    )
    invited_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("researchers.id", ondelete="SET NULL"), nullable=True
    )
    responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    project: Mapped["Project"] = relationship(back_populates="members")
    researcher: Mapped["Researcher"] = relationship("Researcher", foreign_keys=[researcher_id])
    invited_by: Mapped[Optional["Researcher"]] = relationship("Researcher", foreign_keys=[invited_by_id])