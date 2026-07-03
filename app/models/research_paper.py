from sqlalchemy import Column, Integer, String, Text
from app.database.database import Base


class ResearchPaper(Base):
    __tablename__ = "research_papers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    authors = Column(String, nullable=False)
    abstract = Column(Text, nullable=False)
    publication_year = Column(Integer, nullable=False)
    source = Column(String, nullable=False)
    doi = Column(String, unique=True, nullable=False)