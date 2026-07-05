from sqlalchemy import Column, Integer, String
from app.database.database import Base


class Researcher(Base):
    __tablename__ = "researchers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    institution = Column(String(150), nullable=False)
    department = Column(String(100), nullable=False)
    specialization = Column(String(100), nullable=False)
    h_index = Column(Integer, default=0)
    total_publications = Column(Integer, default=0)