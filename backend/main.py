from fastapi import FastAPI
from sqlalchemy import text

from api.auth import router as auth_router

from database.connection import engine
from database.base import Base

from models.user import User
from models.researcher import Researcher

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Scientific Collaboration Network Analyzer",
    version="1.0.0"
)

app.include_router(auth_router)


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
        return {
            "status": "Database connected successfully!"
        }
    except Exception as e:
        return {
            "status": "Connection failed",
            "error": str(e)
        }