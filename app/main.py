from fastapi import FastAPI

from app.routers import research_papers
from app.routers import researchers

app = FastAPI(
    title="Scientific Collaboration Network Analyzer API"
)

app.include_router(research_papers.router)
app.include_router(researchers.router)


@app.get("/")
def home():
    return {
        "message": "Scientific Collaboration Network Analyzer API is Running!"
    }