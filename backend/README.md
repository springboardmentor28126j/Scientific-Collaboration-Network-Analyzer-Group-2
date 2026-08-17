# Backend (FastAPI)

## Setup for local

## macOS:

cd backend
python3 -m venv venv          # first time only
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # first time only, then fill in the values
alembic upgrade head
uvicorn app.main:app --reload --port 8000

## Windows (PowerShell):

cd backend
python -m venv venv           # first time only
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env        # first time only, then fill in the values
alembic upgrade head
uvicorn app.main:app --reload --port 8000

## Running with Docker

Docker Compose is defined at the **project root**, not inside `backend/` — 
run these from the repository root, not from this folder:

```bash
cd ..                       # back to the project root
docker compose build
docker compose up -d
docker compose ps           # backend should show "healthy"
docker compose logs -f backend
```

To build/run just the backend container in isolation (useful for quickly 
checking the Dockerfile itself without spinning up the frontend too):

```bash
docker build -t scna-backend .
docker run --env-file .env -p 8000:8000 scna-backend
```

Either way, health check: http://127.0.0.1:8000/health