import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.routes import (
    admin,
    auth,
    researchers,
    citations,
    collaborations,
    conferences,
    institution,
    publications,
    reviewer_assignments,
    projects,
    audit,
    reports,
    notifications,
)

app = FastAPI(title=settings.PROJECT_NAME)

# Milestone 1: Flask frontend runs on a separate port and calls this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in later milestones once the frontend origin is fixed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads/conference_presentations", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(researchers.router, prefix="/researchers", tags=["researchers"])
app.include_router(conferences.router, prefix="/conferences", tags=["conferences"])
app.include_router(institution.router, prefix="/institutions", tags=["institutions"])
app.include_router(publications.router, prefix="/publications", tags=["publications"])
app.include_router(citations.router, prefix="/citations", tags=["citations"])
app.include_router(collaborations.router, prefix="/collaborations", tags=["collaborations"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(
    reviewer_assignments.router, prefix="/reviewer-assignments", tags=["reviewer-assignments"]
)
app.include_router(projects.router, prefix="/projects", tags=["projects"])
app.include_router(audit.router, prefix="/audit", tags=["audit"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])
app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])


@app.get("/health")
def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}
