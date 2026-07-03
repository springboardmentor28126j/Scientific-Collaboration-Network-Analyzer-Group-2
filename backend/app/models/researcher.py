from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class Researcher(Base):
    __tablename__ = "researchers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    full_name = Column(String, nullable=False)
    department = Column(String)
    institution = Column(String)
    research_interests = Column(String)
    skills = Column(String)
