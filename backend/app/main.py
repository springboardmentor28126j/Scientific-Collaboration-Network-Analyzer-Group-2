import logging
import os
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.logging_config import setup_logging

setup_logging()
error_logger = logging.getLogger("scna.error")
access_logger = logging.getLogger("scna.access")
from app.api.routes import (
    admin,
    assistant,
    auth,
    researchers,
    conferences,
    institution,
    institution_collaborations,
    publications,
    reviewer_assignments,
    citations,
    collaborations,
    reports,
    projects,
    notifications,
    audit_logs,
    messages,
)

app = FastAPI(title=settings.PROJECT_NAME)

# Milestone 1: Flask frontend runs on a separate port and calls this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads/conference_presentations", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(assistant.router, prefix="/assistant", tags=["assistant"])
app.include_router(researchers.router, prefix="/researchers", tags=["researchers"])
app.include_router(conferences.router, prefix="/conferences", tags=["conferences"])
app.include_router(institution.router, prefix="/institutions", tags=["institutions"])
app.include_router(institution_collaborations.router, prefix="/institution-collaborations", tags=["institution-collaborations"])
app.include_router(publications.router, prefix="/publications", tags=["publications"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(
    reviewer_assignments.router, prefix="/reviewer-assignments", tags=["reviewer-assignments"]
)
app.include_router(citations.router, prefix="/citations", tags=["citations"])
app.include_router(collaborations.router, prefix="/collaborations", tags=["collaborations"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])
app.include_router(projects.router, prefix="/projects", tags=["projects"])
app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
app.include_router(audit_logs.router, prefix="/audit-logs", tags=["audit-logs"])
app.include_router(messages.router, prefix="/messages", tags=["messages"])

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000
    client = request.client.host if request.client else "-"
    access_logger.info(
        f"{client} {request.method} {request.url.path} -> {response.status_code} ({duration_ms:.1f}ms)"
    )
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    error_logger.exception(f"Unhandled error on {request.method} {request.url.path}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health")
def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}