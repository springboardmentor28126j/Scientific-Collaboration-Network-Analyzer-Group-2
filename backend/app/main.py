from fastapi import FastAPI
from app.routers import auth, users, researchers, publications, collaborations, conferences, citations, reports, audit, institutions, notifications
from app.database import Base, engine
from app.models import user, researcher, publication, collaboration, conference, citation,report, audit_log, institution, notification
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Scientific Collaboration Network Analyzer")
 
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(researchers.router, prefix="/researchers", tags=["Researchers"])
app.include_router(publications.router, prefix="/publications", tags=["Publications"])
app.include_router(collaborations.router, prefix="/collaborations", tags=["Collaborations"])
app.include_router(conferences.router, prefix="/conferences", tags=["Conferences"])
app.include_router(citations.router, prefix="/citations", tags=["Citations"])
app.include_router(reports.router, prefix="/reports", tags=["Reports"])
app.include_router(institutions.router, prefix="/institutions", tags=["Institutions"])
app.include_router(audit.router, prefix="/audit", tags=["Audit"])
app.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
@app.get("/")
def read_root():
    return {"message": "Scientific Collaboration Network Analyzer API running"}