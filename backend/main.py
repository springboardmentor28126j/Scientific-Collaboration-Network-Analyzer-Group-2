from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models
from database import engine
from auth import router as auth_router
from researchers import router as researchers_router
from files import router as files_router
from file_router import router as file_router
from publication import router as publication_router
from collaboration import router as collaboration_router

app = FastAPI(
    title="Scientific Collaboration Network Analyzer",
    version="1.0.0"
)

# Allow React Frontend to access FastAPI
origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Include all routers
app.include_router(auth_router)
app.include_router(researchers_router)
app.include_router(files_router)
app.include_router(file_router)
app.include_router(publication_router)
app.include_router(collaboration_router)

# Home API
@app.get("/")
def home():
    return {
        "message": "Scientific Collaboration Network Analyzer API is running successfully!"
    }