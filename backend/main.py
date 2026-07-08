from fastapi import FastAPI
from sqlalchemy import text

from database.connection import engine
from database.base import Base

# Import all models
from models.user import User

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Scientific Collaboration Network Analyzer",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Welcome to Scientific Collaboration Network Analyzer!"
    }


@app.get("/test-db")
def test_database():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "Database connected successfully!"}
    except Exception as e:
        return {"status": "Connection failed", "error": str(e)}