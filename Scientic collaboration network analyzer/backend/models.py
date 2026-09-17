from sqlalchemy import Column, Integer, String
from database import Base


class Researcher(Base):
    __tablename__ = "researchers"

    researcher_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    institution = Column(String(150))
    department = Column(String(100))
    country = Column(String(100))


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)


class File(Base):
    __tablename__ = "files"

    file_id = Column(Integer, primary_key=True, index=True)
    researcher_id = Column(Integer)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(255))
    uploaded_set = Column(String(100))