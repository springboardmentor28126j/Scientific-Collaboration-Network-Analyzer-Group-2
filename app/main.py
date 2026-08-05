from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import engine
from app import models

from app.routers import (
    researcher,
    publication,
    institution,
    conference,
    conference_registration,
    project,
    project_members,
    institution_collaboration,
    activity_logs,
    citations,
    reference,
    reports
)

from app.routers.auth import router as auth_router


# ==========================
# Create all database tables
# ==========================

models.Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Scientific Collaboration Network Analyzer API",
    version="0.1.0"
)


# ==========================
# Static Files
# ==========================

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)


# ==========================
# Register Routers
# ==========================

app.include_router(auth_router)


app.include_router(
    researcher.router
)


app.include_router(
    publication.router
)


app.include_router(
    institution.router
)


app.include_router(
    conference.router
)


app.include_router(
    conference_registration.router
)


app.include_router(
    project.router
)


app.include_router(
    project_members.router
)


app.include_router(
    institution_collaboration.router
)


app.include_router(
    activity_logs.router
)


# ==========================
# Citation & Reference Module
# ==========================

app.include_router(
    citations.router
)


app.include_router(
    reference.router
)


# ==========================
# Reports Module
# ==========================

app.include_router(
    reports.router
)


# ==========================
# Root Endpoint
# ==========================

@app.get("/")
def root():

    return {
        "message": "Scientific Collaboration Network Analyzer API is running!"
    }