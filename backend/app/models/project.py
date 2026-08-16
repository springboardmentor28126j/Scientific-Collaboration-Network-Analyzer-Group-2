import enum
from datetime import date, datetime

from sqlalchemy import String, Text, Date, DateTime, func, ForeignKey, Enum, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


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
    __tablename__ = "project"

    project_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus), nullable=False, default=ProjectStatus.PLANNED, server_default="PLANNED"
    )

    lead_researcher_id: Mapped[int] = mapped_column(
        ForeignKey("researcher_profile.researcher_id", ondelete="CASCADE"), nullable=False
    )
    institution_id: Mapped[int | None] = mapped_column(
        ForeignKey("institution.institution_id", ondelete="SET NULL"), nullable=True
    )

    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    lead_researcher: Mapped["ResearcherProfile"] = relationship()
    institution: Mapped["Institution"] = relationship()
    members: Mapped[list["ProjectMember"]] = relationship(back_populates="project", cascade="all, delete-orphan")

    @property
    def member_ids(self) -> list[int]:
        """Only ACCEPTED members -- a pending invite isn't a member yet,
        and a declined one never was."""
        return [m.researcher_id for m in self.members if m.status == ProjectMemberStatus.ACCEPTED]


class ProjectMember(Base):
    """Collaborators on a project. The lead researcher also gets a row here
    (role=LEAD, status=ACCEPTED) so 'who's on this project' is always one
    query. Everyone else starts PENDING when invited and only counts as a
    real member (see Project.member_ids) once they accept."""

    __tablename__ = "project_member"
    __table_args__ = (UniqueConstraint("project_id", "researcher_id", name="uq_project_member"),)

    project_member_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("project.project_id", ondelete="CASCADE"), nullable=False)
    researcher_id: Mapped[int] = mapped_column(
        ForeignKey("researcher_profile.researcher_id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[ProjectMemberRole] = mapped_column(
        Enum(ProjectMemberRole), nullable=False, default=ProjectMemberRole.MEMBER, server_default="MEMBER"
    )
    status: Mapped[ProjectMemberStatus] = mapped_column(
        Enum(ProjectMemberStatus), nullable=False, server_default="ACCEPTED"
    )
    invited_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("researcher_profile.researcher_id", ondelete="SET NULL"), nullable=True
    )
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped["Project"] = relationship(back_populates="members")
    researcher: Mapped["ResearcherProfile"] = relationship(foreign_keys=[researcher_id])
    invited_by: Mapped["ResearcherProfile | None"] = relationship(foreign_keys=[invited_by_id])


class ProjectMessage(Base):
    """The project's group chat. Unlike private Message threads, this has
    no per-user read tracking -- it's a shared room, not a 1:1 inbox.
    Access is gated at the API layer to researchers with an ACCEPTED
    ProjectMember row (lead included)."""

    __tablename__ = "project_message"

    project_message_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("project.project_id", ondelete="CASCADE"), nullable=False)
    sender_id: Mapped[int] = mapped_column(
        ForeignKey("researcher_profile.researcher_id", ondelete="CASCADE"), nullable=False
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_project_message_project_created", "project_id", "created_at"),
    )

    project: Mapped["Project"] = relationship()
    sender: Mapped["ResearcherProfile"] = relationship()