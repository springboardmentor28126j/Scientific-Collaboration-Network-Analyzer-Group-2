from fastapi import FastAPI
from app.database import engine
from app import models
from fastapi.staticfiles import StaticFiles
from app.routers import (
    researcher,
    publication,
    institution,
    conference,
    conference_registration
)
from app.routers.auth import router as auth_router

# Create all database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Scientific Collaboration Network Analyzer API",
    version="0.1.0"
)
app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)

# Register routers
app.include_router(auth_router)
app.include_router(researcher.router)
app.include_router(publication.router)
app.include_router(institution.router)
app.include_router(conference.router)
app.include_router(conference_registration.router)


@app.get("/")
def root():
    return {
        "message": "Scientific Collaboration Network Analyzer API is running!"
    }