# Frontend (Flask) — Milestone 1

## Setup
```bash
cd frontend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Run
```bash
python app.py
```
Visit http://127.0.0.1:5000

## Current status
Wired to the backend: login, register, dashboard, and profile all call the
FastAPI API (`BACKEND_URL`, default `http://127.0.0.1:8000`). The JWT access
token is stored in the Flask session after login/register+login.

Start the backend first (see `../backend/README.md`), then run this app.
