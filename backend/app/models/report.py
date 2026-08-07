from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    researcher_id = Column(Integer, ForeignKey("researchers.id"), nullable=False)
    report_type = Column(String(50), nullable=False)  # publication, research, collaboration, institution
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Report data
    total_count = Column(Integer, default=0)
    year_range = Column(String(50), nullable=True)  # e.g., "2020-2024"
    summary = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    researcher = relationship("Researcher", backref="reports")