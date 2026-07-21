from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

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

    keywords = Column(String)

    paper_file = Column(String)

    status = Column(String, default="Draft")

    researcher_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    researcher = relationship(
        "User",
        back_populates="papers"
    )