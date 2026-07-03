from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
import enum

class PublicationType(str, enum.Enum):
    JOURNAL_PAPER = "journal_paper"
    CONFERENCE_PAPER = "conference_paper"
    BOOK = "book"
    PATENT = "patent"
    TECHNICAL_REPORT = "technical_report"

class PublicationStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class Publication(Base):
    __tablename__ = "publications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    type = Column(Enum(PublicationType), nullable=False)
    status = Column(Enum(PublicationStatus), default=PublicationStatus.DRAFT)
    doi = Column(String, unique=True, nullable=True)
    file_path = Column(String, nullable=True)
    author_id = Column(Integer, ForeignKey("researchers.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
