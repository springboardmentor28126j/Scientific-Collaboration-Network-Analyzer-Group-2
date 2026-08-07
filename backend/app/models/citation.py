from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Citation(Base):
    __tablename__ = "citations"

    id = Column(Integer, primary_key=True, index=True)
    citing_publication_id = Column(Integer, ForeignKey("publications.id"), nullable=False)
    cited_publication_id = Column(Integer, ForeignKey("publications.id"), nullable=False)
    
    # Citation metadata
    title = Column(String(255), nullable=True)
    authors = Column(String(500), nullable=True)
    journal = Column(String(255), nullable=True)
    year = Column(Integer, nullable=True)
    doi = Column(String(255), nullable=True)
    citation_style = Column(String(50), default="APA")  # APA, IEEE, BibTeX
    formatted_citation = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    citing_publication = relationship("Publication", foreign_keys=[citing_publication_id])
    cited_publication = relationship("Publication", foreign_keys=[cited_publication_id])