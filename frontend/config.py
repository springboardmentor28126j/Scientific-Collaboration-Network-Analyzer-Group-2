import os

BACKEND_API_URL = os.environ.get("BACKEND_API_URL", "http://localhost:8000/api/v1")
FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")
