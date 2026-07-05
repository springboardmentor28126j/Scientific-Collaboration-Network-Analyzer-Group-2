from sqlalchemy import Column, Integer, String
from app.database.database import Base


class Institution(Base):
    __tablename__ = "institutions"

    id = Column(Integer, primary_key=True, index=True)
    institution_name = Column(String(150), nullable=False)
    country = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    website = Column(String(200), nullable=True)
    established_year = Column(Integer, nullable=True)