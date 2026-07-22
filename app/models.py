from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from .database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String(100), nullable=False)

    email = Column(String(100), unique=True, nullable=False)

    password = Column(String(255), nullable=False)

    role = Column(String(50), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

class Researcher(Base):
    __tablename__ = "researchers"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True
    )

    full_name = Column(String(100), nullable=False)

    email = Column(
        String(100),
        unique=True,
        nullable=False
    )

    department = Column(String(100), nullable=False)

    institution = Column(String(150), nullable=False)

    designation = Column(String(100), nullable=False)

    research_interests = Column(String(255), nullable=True)

    skills = Column(String(255), nullable=True)

    phone = Column(String(20), nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    publications = relationship(
        "Publication",
        back_populates="researcher"
    )
class Publication(Base):
    __tablename__ = "publications"

    id = Column(Integer, primary_key=True, index=True)

    researcher_id = Column(
        Integer,
        ForeignKey("researchers.id")
    )

    title = Column(String(255), nullable=False)

    publication_type = Column(String(100), nullable=False)

    journal_name = Column(String(255))

    conference_name = Column(String(255))

    publication_year = Column(Integer)

    doi = Column(String(100))

    status = Column(String(50))

    publication_file = Column(String(255))

    created_at = Column(DateTime, default=datetime.utcnow)


    researcher = relationship("Researcher")
class Institution(Base):

    __tablename__ = "institutions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True
    )

    name = Column(
        String(150),
        nullable=False
    )

    institution_type = Column(
        String(100)
    )

    location = Column(
        String(150),
        nullable=False
    )

    website = Column(
        String(255)
    )

    phone = Column(
        String(20)
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
class Conference(Base):

    __tablename__ = "conferences"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    title = Column(
        String(255),
        nullable=False
    )


    organizer = Column(
        String(255),
        nullable=False
    )


    location = Column(
        String(150),
        nullable=False
    )


    conference_date = Column(
        String(50),
        nullable=False
    )


    website = Column(
        String(255)
    )


    institution = Column(
        String(150)
    )


    event_type = Column(
        String(100)
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )