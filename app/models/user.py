from sqlalchemy import Column, Integer, String, Date
from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Basic Details
    full_name = Column(String(150), nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # Personal Details
    phone_number = Column(String(20))
    gender = Column(String(20))
    date_of_birth = Column(Date)

    # Academic Details
    institution = Column(String(150))
    department = Column(String(100))
    designation = Column(String(100))

    # Research Details
    specialization = Column(String(150))
    research_interests = Column(String(255))

    # Location
    country = Column(String(100))
    state = Column(String(100))
    city = Column(String(100))

    website = Column(String(255))
    established_year = Column(String(10))
    institution_type = Column(String(100))

    # Role
    role = Column(String(50), default="Researcher")