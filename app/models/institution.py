from datetime import datetime

from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Institution(Base):
    __tablename__ = "institution"

    institution_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(100), nullable=True)  # university, lab, publisher, funding_org
    country: Mapped[str] = mapped_column(String(100), nullable=True)
    address: Mapped[str] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    email_domain: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)
    departments: Mapped[list["Department"]] = relationship(back_populates="institution", cascade="all, delete-orphan")
    users: Mapped[list["User"]] = relationship(back_populates="institution")


class Department(Base):
    __tablename__ = "department"

    department_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    institution_id: Mapped[int] = mapped_column(ForeignKey("institution.institution_id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=True)

    institution: Mapped["Institution"] = relationship(back_populates="departments")
    researchers: Mapped[list["ResearcherProfile"]] = relationship(back_populates="department")
