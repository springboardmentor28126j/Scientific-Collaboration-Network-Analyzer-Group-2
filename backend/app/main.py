from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import auth, researchers

app = FastAPI(title=settings.PROJECT_NAME)

# Milestone 1: Flask frontend runs on a separate port and calls this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in later milestones once the frontend origin is fixed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(researchers.router, prefix="/researchers", tags=["researchers"])


@app.get("/health")
def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}
