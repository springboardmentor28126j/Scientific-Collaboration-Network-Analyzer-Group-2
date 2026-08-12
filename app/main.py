from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database.database import Base, engine
from app.models import user

from app.routers import research_papers
from app.routers import researchers
from app.routers import institutions
from app.routers import collaborations
from app.routers import analytics
from app.routers import auth
from app.routers import conferences
from app.routers import dashboard
from app.routers import citations
from app.routers import projects
from app.routers import project_members
from app.routers import project_milestones
from app.routers import project_tasks
from app.routers import activity_logs
from app.routers import network
from app.models.project_document import ProjectDocument
from app.routers import project_documents
from app.models.project_comment import ProjectComment
from app.routers import project_comments
from app.models.notification import Notification
from app.routers import notifications
from app.models.collaboration_request import CollaborationRequest
from app.routers import collaboration_requests
from app.models.institution_collaboration_request import InstitutionCollaborationRequest
from app.routers import institution_collaboration_requests
from app.models.project_timeline import ProjectTimeline
from app.routers import project_timelines
from app.models import audit_log
from app.routers import audit_logs
from app.models.audit_log import AuditLog
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Scientific Collaboration Network Analyzer API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Serve uploaded PDF files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(research_papers.router)
app.include_router(researchers.router)
app.include_router(institutions.router)
app.include_router(collaborations.router)
app.include_router(citations.router)
app.include_router(analytics.router)
app.include_router(auth.router)
app.include_router(conferences.router)
app.include_router(dashboard.router)
app.include_router(projects.router)
app.include_router(project_members.router)
app.include_router(project_milestones.router)
app.include_router(project_tasks.router)
app.include_router(activity_logs.router)
app.include_router(network.router)
app.include_router(project_documents.router)
app.include_router(project_comments.router)
app.include_router(notifications.router)
app.include_router(collaboration_requests.router)
app.include_router(
    institution_collaboration_requests.router
)
app.include_router(project_timelines.router)
app.include_router(audit_logs.router)

@app.get("/")
def home():
    return {
        "message": "Scientific Collaboration Network Analyzer API is Running!"
    }