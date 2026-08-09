# Backend (FastAPI) 

## Setup

# Navigate to backend folder
cd "Scientific-Collaboration-Network-Analyzer-Group-2/backend"

# --- First time only ---
source venv/bin/activate
pip install -r requirements.txt

alembic upgrade head
uvicorn app.main:app --reload --port 8000


`DATABASE_URL` in `.env.example` points at PostgreSQL. Make sure a local
PostgreSQL server is running and the `scna` database/user in the URL exist
before running migrations, e.g.:
```sql
CREATE USER scna_user WITH PASSWORD 'scna_password';
CREATE DATABASE scna OWNER scna_user;
```
— Milestone 1

## Run migrations
```bash
alembic upgrade head
```
This creates `users`, `institutions`, and `researchers` tables (see `../SCHEMA.md`).

## Run the API
```bash
uvicorn app.main:app --reload --port 8000
```
Health check: http://127.0.0.1:8000/health
Interactive docs: http://127.0.0.1:8000/docs

## Endpoints (Milestone 1)
- `POST /auth/register` — create a user (defaults to researcher role)
- `POST /auth/login` — OAuth2 password flow, returns a JWT access token
- `GET /researchers/me` — get the logged-in researcher's profile (auth required)
- `POST /researchers/me` — create the logged-in researcher's profile (auth required)
- `PUT /researchers/me` — update the logged-in researcher's profile (auth required)
