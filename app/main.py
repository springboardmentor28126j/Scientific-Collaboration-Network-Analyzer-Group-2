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
app.include_router(analytics.router)
app.include_router(auth.router)
app.include_router(conferences.router)
app.include_router(dashboard.router)

@app.get("/")
def home():
    return {
        "message": "Scientific Collaboration Network Analyzer API is Running!"
    }