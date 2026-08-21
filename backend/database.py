from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# PostgreSQL Database URL
DATABASE_URL = "postgresql://postgres:root@localhost:5432/scientific_collaboration"

# Create database engine
engine = create_engine(DATABASE_URL)

# Create database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all models
Base = declarative_base()


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()