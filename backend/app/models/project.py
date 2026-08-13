import enum
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, utcnow


class ProjectStatus(str, enum.Enum):
    """Vocabulary matches the real 'projectstatus' Postgres enum type
    already present in the shared DB (see check_vocab.py diagnostic) --
    not this project's original planning/active/on_hold/completed design,
    which was reverted by an external migration chain sharing this DB.
    Adopted as-is rather than fought again."""

    PLANNED = "planned"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectRole(str, enum.Enum):
    """Matches the real 'projectmemberrole' Postgres enum type, which only
    has two labels -- no CO_INVESTIGATOR distinction in the shared DB."""

    LEAD = "lead"
    MEMBER = "member"


class ProjectMemberStatus(str, enum.Enum):
    """Matches the real 'projectmemberstatus' Postgres enum type already
    present in the shared DB (project_members.status, invited_by_id,
    responded_at columns all pre-exist there from the reference chain --
    confirmed via a diagnostic before adding these mappings, same pattern
    used for AuthToken/auth_tokens). An invite starts PENDING; the invitee
    flips it to ACCEPTED or DECLINED. The lead's own row is created
    ACCEPTED directly -- a lead never goes through the invite step."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"


class Project(Base):
    """A funded/ongoing research project (Module 4: Collaboration Management
    -> Research projects / Project assignments). Distinct from
    CollaborationRequest/Collaboration (peer-to-peer network edges): a
    Project is a durable, named body of work with a lead, a team, and an
    optional funding source."""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, values_callable=lambda enum_cls: [m.value for m in enum_cls]),
        default=ProjectStatus.PLANNED,
        nullable=False,
    )
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    # NOTE: funding_source/budget were removed -- the shared DB's projects
    # table (reconciled from an external migration chain) doesn't have
    # these columns. Re-add here + in schemas/project.py + the migration
    # if a future ALTER TABLE against that DB adds them back.

    institution_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("institutions.id"), nullable=True
    )
    lead_researcher_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("researchers.id"), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, onupdate=utcnow, nullable=False
    )

    institution: Mapped["Institution"] = relationship("Institution")
    lead_researcher: Mapped["Researcher"] = relationship(
        "Researcher", foreign_keys=[lead_researcher_id]
    )
    members: Mapped[list["ProjectMember"]] = relationship(
        "ProjectMember", back_populates="project", cascade="all, delete-orphan"
    )

    @property
    def member_ids(self) -> list[int]:
        """Researcher ids with an ACCEPTED membership. A pending invite
        or a declined one isn't a member yet/anymore -- used to gate
        both project visibility and 'who's on the team' displays."""
        return [
            m.researcher_id for m in self.members if m.status == ProjectMemberStatus.ACCEPTED
        ]


class ProjectMember(Base):
    """Team assignment: which researchers are on a project and in what
    capacity. The lead researcher is not auto-added here -- routes add
    them as a LEAD member on project creation, same pattern as
    PublicationAuthor auto-adding the creating researcher."""

    __tablename__ = "project_members"
    __table_args__ = (
        UniqueConstraint("project_id", "researcher_id", name="uq_project_researcher"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=False
    )
    researcher_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("researchers.id"), nullable=False
    )
    role_in_project: Mapped[ProjectRole] = mapped_column(
        "role",
        Enum(ProjectRole, values_callable=lambda enum_cls: [m.value for m in enum_cls]),
        default=ProjectRole.MEMBER,
        nullable=False,
    )
    status: Mapped[ProjectMemberStatus] = mapped_column(
        Enum(
            ProjectMemberStatus,
            values_callable=lambda enum_cls: [m.value for m in enum_cls],
            name="projectmemberstatus",
        ),
        default=ProjectMemberStatus.PENDING,
        nullable=False,
    )
    invited_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("researchers.id"), nullable=True
    )
    responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="members")
    researcher: Mapped["Researcher"] = relationship("Researcher", foreign_keys=[researcher_id])
