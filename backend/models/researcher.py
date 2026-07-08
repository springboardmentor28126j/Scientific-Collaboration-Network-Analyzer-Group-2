from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database.base import Base


class Researcher(Base):
    __tablename__ = "researchers"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    full_name = Column(String, nullable=False)

    institution = Column(String)

    department = Column(String)

    designation = Column(String)

    research_interest = Column(String)

    skills = Column(String)

    bio = Column(String)

    user = relationship(
        "User",
        back_populates="researcher"
    )