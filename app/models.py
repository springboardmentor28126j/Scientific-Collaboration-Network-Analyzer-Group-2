from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)

class Researcher(Base):
    __tablename__ = "researchers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    department = Column(String, nullable=False)
    institution = Column(String, nullable=False)
    institution_id = Column(
    Integer,
    ForeignKey("institutions.id"),
    nullable=True
    )
    skills = Column(String, nullable=True)
    research_interest = Column(String, nullable=True)
    designation = Column(String, nullable=False)

class Institution(Base):
    __tablename__ = "institutions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    address = Column(String, nullable=True)
    website = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)

class Publication(Base):
    __tablename__ = "publications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    abstract = Column(String, nullable=True)

    # journal_paper, conference_paper, book, patent, technical_report
    publication_type = Column(String, nullable=False)

    # draft, submitted, published, archived
    status = Column(String, nullable=False, default="draft")

    doi = Column(String, unique=True, nullable=True)
    publication_date = Column(Date, nullable=True)
    journal_or_venue = Column(String, nullable=True)
    file_path = Column(String, nullable=True)

    institution_id = Column(
        Integer,
        ForeignKey("institutions.id"),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )