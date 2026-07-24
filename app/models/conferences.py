from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Conference(Base):
    __tablename__ = "conferences"

    id = Column(Integer, primary_key=True, index=True)

    conference_name = Column(String, nullable=False)

    organizer = Column(String, nullable=False)

    venue = Column(String, nullable=False)

    country = Column(String, nullable=False)

    conference_date = Column(Date, nullable=False)

    submission_deadline = Column(Date, nullable=False)

    registration_deadline = Column(Date, nullable=False)

    registration_fee = Column(Integer, nullable=False)

    conference_type = Column(String, nullable=False)

    website = Column(String)

    description = Column(Text)

    topics = Column(String)

    banner_image = Column(String)

    brochure_pdf = Column(String)

    status = Column(String, default="Upcoming")

    researcher_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    researcher = relationship(
        "User",
        back_populates="conferences"
    )