from fastapi import FastAPI
from app.routers import research_papers

app = FastAPI(
    title="Scientific Collaboration Network Analyzer API"
)

app.include_router(research_papers.router)


@app.get("/")
def home():
    return {
        "message": "Scientific Collaboration Network Analyzer API is Running!"
    }