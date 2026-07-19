from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.database import engine, Base
import app.models
from app.routes import users, researchers, institutions
import traceback

app = FastAPI(title="Scientific Collaboration Network Analyzer")
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

@app.get("/")
def root():
    return {"status": "Project started successfully"}