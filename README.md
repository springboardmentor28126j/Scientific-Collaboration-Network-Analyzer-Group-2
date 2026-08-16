# Scientific Collaboration Network Analyzer

Milestone 1 implementation (Week 1-2): Authentication, User Management, Researcher Profiles.

## Stack

- **Backend:** FastAPI + SQLAlchemy + Alembic + PostgreSQL + Redis + JWT auth
- **Frontend:** Flask (server-rendered HTML, session-based auth against the backend's JWT API)
- **Deployment:** Docker Compose

## Quick Start (Docker)

```bash
cp backend/.env.example backend/.env
# edit backend/.env and set a real JWT_SECRET_KEY

docker compose up --build
```

- Backend API: http://localhost:8000 (interactive docs at http://localhost:8000/docs)
- Frontend: http://localhost:5000

## Quick Start (local, no Docker)

**Backend**
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # point DATABASE_URL at a local Postgres, or use sqlite for quick testing
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend** (in a second terminal)
```bash
cd frontend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export BACKEND_API_URL=http://localhost:8000/api/v1
python app.py
```

## What's implemented in this milestone

- User registration & JWT login/refresh (`/api/v1/auth/*`)
- **Redis-backed session store**: every access/refresh token is tied to a Redis key with a TTL matching its JWT expiry. `/auth/logout` deletes the key, so tokens are revoked immediately instead of staying valid until they naturally expire. `/auth/refresh` rotates the refresh token (old one is single-use) and returns a brand new pair.
- Role-based access control: researcher, institution_admin, reviewer, system_admin
- Institution & department management
- Researcher profile CRUD, skills, and research interests
- Researcher search/directory
- Audit logging on every create/update/delete/login action
- Flask UI: register, login, dashboard, profile editor, researcher directory

## What's coming in later milestones

- Publication management (Milestone 2)
- Conference management (Milestone 2)
- Collaboration/project tracking, citations (Milestone 3)
- Reports, dashboards, exports (Milestone 3)
- Testing, performance tuning, final Docker hardening (Milestone 4)

## Project layout

See `docs/architecture/architecture_week1.md` for the full architecture writeup (requirements, ER diagram, API design, folder structure rationale).
