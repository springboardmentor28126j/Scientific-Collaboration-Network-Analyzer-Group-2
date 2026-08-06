from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, func
from sqlalchemy import Table
from sqlalchemy.orm import relationship
from app.database import Base


# ✅ ASSOCIATION TABLE (Many-to-Many)
publication_authors = Table(
    "publication_authors",
    Base.metadata,
    Column("publication_id", Integer, ForeignKey("publications.id"), primary_key=True),
    Column("researcher_id", Integer, ForeignKey("researchers.id"), primary_key=True)
)


# ---------------- USERS ----------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    requested_role = Column(String, nullable=True)
    account_status = Column(String, nullable=False, default="active")

    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String, nullable=False, default="system")
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    link = Column(String, nullable=True)
    is_read = Column(Integer, nullable=False, default=0)
    email_sent = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="notifications")


# ---------------- INSTITUTIONS ----------------
class Institution(Base):
    __tablename__ = "institutions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String)
    website = Column(String)
    contact_email = Column(String)

    # ✅ relationship
    researchers = relationship("Researcher", back_populates="institution", cascade="all, delete")


# ---------------- RESEARCHERS ----------------
class Researcher(Base):
    __tablename__ = "researchers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    department = Column(String)
    skills = Column(String)
    research_interest = Column(String)
    designation = Column(String)
    email = Column(String, nullable=True, unique=True)

    institution_id = Column(Integer, ForeignKey("institutions.id"))

    # ✅ relationships
    institution = relationship("Institution", back_populates="researchers")

    publications = relationship(
        "Publication",
        secondary=publication_authors,
        back_populates="authors"
    )


# ---------------- PUBLICATIONS ----------------
class Publication(Base):
    __tablename__ = "publications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    abstract = Column(String)
    file_path = Column(String)

    doi = Column(String, unique=True, nullable=True)
    publication_type = Column(String)
    status = Column(String, default="draft")
    publication_date = Column(Date)
    journal_or_venue = Column(String)

    institution_id = Column(Integer, ForeignKey("institutions.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ✅ MANY-TO-MANY RELATIONSHIP
    authors = relationship(
        "Researcher",
        secondary=publication_authors,
        back_populates="publications"
    )


# ---------------- CONFERENCES ----------------
class Conference(Base):
    __tablename__ = "conferences"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)

    participants = relationship(
        "ConferenceParticipation",
        back_populates="conference",
        cascade="all, delete"
    )


# ---------------- CONFERENCE PARTICIPATION ----------------
class ConferenceParticipation(Base):
    __tablename__ = "conference_participation"

    id = Column(Integer, primary_key=True, index=True)
    researcher_id = Column(Integer, ForeignKey("researchers.id"))
    conference_id = Column(Integer, ForeignKey("conferences.id"))
    presentation_title = Column(String)

    researcher = relationship("Researcher")
    conference = relationship("Conference", back_populates="participants")


class Collaboration(Base):
    __tablename__ = "collaborations"

    id = Column(Integer, primary_key=True, index=True)

    researcher1_id = Column(
        Integer,
        ForeignKey("researchers.id")
    )

    researcher2_id = Column(
        Integer,
        ForeignKey("researchers.id")
    )

    publication_id = Column(
        Integer,
        ForeignKey("publications.id")
    )

    project = Column(String, nullable=True)
    status = Column(String, nullable=False, default="pending")
    requested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    responded_at = Column(DateTime(timezone=True), nullable=True)

    researcher1 = relationship(
        "Researcher",
        foreign_keys=[researcher1_id]
    )

    researcher2 = relationship(
        "Researcher",
        foreign_keys=[researcher2_id]
    )

    publication = relationship(
        "Publication",
        foreign_keys=[publication_id]
    )

class Citation(Base):
    __tablename__ = "citations"

    id = Column(Integer, primary_key=True, index=True)
    citing_publication_id = Column(
        Integer,
        ForeignKey("publications.id"),
        nullable=False
    )
    cited_publication_id = Column(
        Integer,
        ForeignKey("publications.id"),
        nullable=False
    )

    citing_publication = relationship(
        "Publication",
        foreign_keys=[citing_publication_id]
    )
    cited_publication = relationship(
        "Publication",
        foreign_keys=[cited_publication_id]
    )


class GeneratedReport(Base):
    __tablename__ = "generated_reports"

    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"), unique=True, nullable=False)
    researchers = Column(Integer, nullable=False, default=0)
    publications = Column(Integer, nullable=False, default=0)
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    institution = relationship("Institution")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=True)
    details = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User")


# ---------------- PROJECTS ----------------
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    funding_agency = Column(String, nullable=True)
    status = Column(String, nullable=False, default="planned")
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=True)

    assignments = relationship(
        "ProjectAssignment",
        back_populates="project",
        cascade="all, delete-orphan"
    )


class ProjectAssignment(Base):
    __tablename__ = "project_assignments"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    researcher_id = Column(Integer, ForeignKey("researchers.id"), nullable=False)
    role = Column(String, nullable=False, default="Member")

    project = relationship("Project", back_populates="assignments")
    researcher = relationship("Researcher")
