import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# This creates an absolute path to the project folder database file.
PROJECT_FOLDER = Path(__file__).resolve().parent.parent
DATABASE_FILE = PROJECT_FOLDER / "research_network.db"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{DATABASE_FILE.as_posix()}"
)

print("USING DATABASE:", DATABASE_URL)  # 👈 ADD THIS


connect_args = (
    {"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()