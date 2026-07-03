from fastapi import FastAPI

from app.routers import auth

app = FastAPI(
    title="Scientific Collaboration Network Analyzer API"
)

app.include_router(auth.router)


@app.get("/")
def home():
    return {
        "message": "Welcome to Scientific Collaboration Network Analyzer API"
    }