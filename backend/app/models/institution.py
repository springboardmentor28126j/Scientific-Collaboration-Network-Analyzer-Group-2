from sqlalchemy import Column, Integer, String
from app.database import Base

class Institution(Base):
    __tablename__ = "institutions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=True)
    location = Column(String, nullable=True)
    website = Column(String, nullable=True)
    description = Column(String, nullable=True)