from sqlalchemy import Column, Integer, ForeignKey
from app.database import Base

class Citation(Base):
    __tablename__ = "citations"

    id = Column(Integer, primary_key=True, index=True)
    citing_publication_id = Column(Integer, ForeignKey("publications.id"))
    cited_publication_id = Column(Integer, ForeignKey("publications.id"))
