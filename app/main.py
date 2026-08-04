from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.database import engine, Base
import app.models
from app.routes import users, researchers, institutions, publications, conferences
from app.routes import collaborations, dashboard, reports, citations, projects, notifications


app = FastAPI(title="Scientific Collaboration Network Analyzer")

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

app.mount("/files", StaticFiles(directory=str(UPLOADS_DIR)), name="files")

app.mount("/frontend", StaticFiles(directory=str(BASE_DIR / "frontend")), name="frontend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.create_all(bind=engine)



app.include_router(users.router)
app.include_router(researchers.router)
app.include_router(institutions.router)
app.include_router(publications.router)
app.include_router(conferences.router)
app.include_router(collaborations.router)
app.include_router(dashboard.router)
app.include_router(reports.router)
app.include_router(citations.router)
app.include_router(projects.router)
app.include_router(notifications.router)

@app.get("/")
def root():
    return {"status": "Project started successfully"}
