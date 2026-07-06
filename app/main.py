from fastapi import FastAPI

from app.routers import research_papers
from app.routers import researchers
from app.routers import institutions
from app.routers import collaborations
from app.routers import analytics

app = FastAPI(
    title="Scientific Collaboration Network Analyzer API"
)

app.include_router(research_papers.router)
app.include_router(researchers.router)
app.include_router(institutions.router)
app.include_router(collaborations.router)
app.include_router(analytics.router)


@app.get("/")
def home():
    return {
        "message": "Scientific Collaboration Network Analyzer API is Running!"
    }