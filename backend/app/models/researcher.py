from datetime import datetime

from sqlalchemy import String, DateTime, func, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ResearcherProfile(Base):
    __tablename__ = "researcher_profile"

    researcher_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id", ondelete="CASCADE"), unique=True)
    department_id: Mapped[int | None] = mapped_column(
        ForeignKey("department.department_id", ondelete="SET NULL"), nullable=True
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    academic_title: Mapped[str] = mapped_column(String(100), nullable=True)
    orcid_id: Mapped[str] = mapped_column(String(50), nullable=True)
    bio: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="researcher_profile")
    department: Mapped["Department"] = relationship(back_populates="researchers")

    skills: Mapped[list["ResearcherSkill"]] = relationship(back_populates="researcher", cascade="all, delete-orphan")
    interests: Mapped[list["ResearcherInterest"]] = relationship(back_populates="researcher", cascade="all, delete-orphan")

    @property
    def skill_objects(self) -> list["Skill"]:
        """Flattens the researcher_skill join rows into plain Skill objects for API responses."""
        return [rs.skill for rs in self.skills]

    @property
    def interest_objects(self) -> list["ResearchInterest"]:
        """Flattens the researcher_interest join rows into plain ResearchInterest objects for API responses."""
        return [ri.interest for ri in self.interests]


class Skill(Base):
    __tablename__ = "skill"

    skill_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)


class ResearcherSkill(Base):
    __tablename__ = "researcher_skill"
    __table_args__ = (UniqueConstraint("researcher_id", "skill_id", name="uq_researcher_skill"),)

    researcher_skill_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    researcher_id: Mapped[int] = mapped_column(ForeignKey("researcher_profile.researcher_id", ondelete="CASCADE"))
    skill_id: Mapped[int] = mapped_column(ForeignKey("skill.skill_id", ondelete="CASCADE"))

    researcher: Mapped["ResearcherProfile"] = relationship(back_populates="skills")
    skill: Mapped["Skill"] = relationship()


class ResearchInterest(Base):
    __tablename__ = "research_interest"

    interest_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)


class ResearcherInterest(Base):
    __tablename__ = "researcher_interest"
    __table_args__ = (UniqueConstraint("researcher_id", "interest_id", name="uq_researcher_interest"),)

    researcher_interest_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    researcher_id: Mapped[int] = mapped_column(ForeignKey("researcher_profile.researcher_id", ondelete="CASCADE"))
    interest_id: Mapped[int] = mapped_column(ForeignKey("research_interest.interest_id", ondelete="CASCADE"))

    researcher: Mapped["ResearcherProfile"] = relationship(back_populates="interests")
    interest: Mapped["ResearchInterest"] = relationship()
