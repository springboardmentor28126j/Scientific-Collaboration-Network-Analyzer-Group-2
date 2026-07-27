from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
import app.models
from app.routes import users, researchers, institutions, publications, conferences
from app.routes import collaborations


app = FastAPI(title="Scientific Collaboration Network Analyzer")


app.mount("/files", StaticFiles(directory="uploads"), name="files")

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

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

@app.get("/")
def root():
    return {"status": "Project started successfully"}
