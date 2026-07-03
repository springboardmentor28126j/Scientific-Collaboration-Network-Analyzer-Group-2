from sqlalchemy import Column, Integer, String, Date, ForeignKey
from app.database import Base

class Conference(Base):
    __tablename__ = "conferences"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)

class ConferenceParticipation(Base):
    __tablename__ = "conference_participation"

    id = Column(Integer, primary_key=True, index=True)
    conference_id = Column(Integer, ForeignKey("conferences.id"))
    researcher_id = Column(Integer, ForeignKey("researchers.id"))
    presentation_title = Column(String, nullable=True)
