# Frontend (Flask) — Milestone 1

## Setup

# Navigate to frontend folder
cd "C:\Users\yella\Group1\Infosys Internship\internship\frontend"

# --- First time only ---
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# --- Every time you open a new terminal ---
.\venv\Scripts\Activate.ps1
python app.py


{deactivate
cd "C:\Users\yella\Group1\Infosys Internship\frontend"
.venv\Scripts\activate
python -m pip install -r requirements.txt
python app.py}

Visit http://127.0.0.1:5000

## Current status
Wired to the backend: login, register, dashboard, and profile all call the
FastAPI API (`BACKEND_URL`, default `http://127.0.0.1:8000`). The JWT access
token is stored in the Flask session after login/register+login.

Start the backend first (see `../backend/README.md`), then run this app.
