from sqlalchemy import Column, Integer, ForeignKey
from app.database.database import Base


class Collaboration(Base):
    __tablename__ = "collaborations"

    id = Column(Integer, primary_key=True, index=True)

    researcher_1_id = Column(
        Integer,
        ForeignKey("researchers.id"),
        nullable=False
    )

    researcher_2_id = Column(
        Integer,
        ForeignKey("researchers.id"),
        nullable=False
    )

    paper_id = Column(
        Integer,
        ForeignKey("research_papers.id"),
        nullable=False
    )

    collaboration_year = Column(Integer, nullable=False)