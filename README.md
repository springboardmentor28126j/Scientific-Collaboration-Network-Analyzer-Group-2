# Scientific Collaboration Network Analyzer

Research collaboration management platform for universities and research organizations
(publications, researchers, institutions, projects, conferences, and collaborations).

This repo currently implements **Module 1: User Management** (Milestone 1 scope):
roles, registration, JWT login, researcher profiles, and institution management.
Modules 2-9 (Researcher/Publication/Collaboration/Conference/Citation management,
Dashboards, Reports, Audit) are not yet built.

## Tech stack

- **Backend**: Python, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2
- **Auth**: JWT (python-jose), bcrypt password hashing (passlib)
- **Database**: PostgreSQL (Docker), SQLite supported for local dev
- **Deployment**: Docker / docker-compose

## Module 1 scope

**Roles**: Researcher, Institution Admin, Reviewer, System Admin

**Features**: Login, Registration, Researcher Profile, Institution Management

## Project structure

```
backend/
  app/
    core/       # settings, JWT + password hashing
    db/         # SQLAlchemy engine/session, declarative base
    models/     # User, Institution, ResearcherProfile
    schemas/    # Pydantic request/response models
    crud/       # DB access functions
    api/        # routes + auth/RBAC dependencies
    main.py     # FastAPI app
  alembic/      # DB migrations
  Dockerfile
docker-compose.yml
```

## Running with Docker (recommended)

```bash
docker compose up --build
```

The API will be available at http://localhost:8000, with interactive docs at
http://localhost:8000/docs. Migrations run automatically on container start.

## Running locally without Docker

Requires Python 3.12 (psycopg2-binary and pydantic-core wheels are not yet published
for newer Python versions such as 3.14).

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate   # Windows
pip install -r requirements.txt

# Point at a local Postgres, or use SQLite for quick local testing:
export DATABASE_URL="sqlite:///./dev.db"
export SECRET_KEY="dev-secret-key"

alembic upgrade head
uvicorn app.main:app --reload
```

## API overview

| Method | Endpoint                          | Access                              | Purpose                       |
|--------|------------------------------------|--------------------------------------|--------------------------------|
| POST   | `/api/v1/auth/register`            | Public                               | Register a user                |
| POST   | `/api/v1/auth/login`               | Public                               | Login, returns JWT              |
| GET    | `/api/v1/users/me`                 | Authenticated                        | Current user + profile         |
| PUT    | `/api/v1/users/me`                 | Authenticated                        | Update own basic info          |
| GET    | `/api/v1/users/`                   | System Admin                         | List all users                 |
| GET    | `/api/v1/users/{id}`               | System Admin / Institution Admin     | Get a user                     |
| GET    | `/api/v1/researchers/me`           | Authenticated                        | Get own researcher profile     |
| PUT    | `/api/v1/researchers/me`           | Authenticated                        | Update own researcher profile  |
| GET    | `/api/v1/researchers/`             | Authenticated                        | List researcher profiles       |
| GET    | `/api/v1/researchers/{user_id}`    | Authenticated                        | Get a researcher profile       |
| POST   | `/api/v1/institutions/`            | System Admin                         | Create institution              |
| GET    | `/api/v1/institutions/`            | Authenticated                        | List institutions               |
| GET    | `/api/v1/institutions/{id}`        | Authenticated                        | Get an institution              |
| PUT    | `/api/v1/institutions/{id}`        | System Admin / owning Institution Admin | Update an institution        |
| DELETE | `/api/v1/institutions/{id}`        | System Admin                         | Delete an institution           |

Registering with `role: researcher` or `role: reviewer` is open to the public and, for
researchers, automatically creates an empty researcher profile. Self-registration as
`institution_admin` or `system_admin` is blocked (`400`) — those accounts must be
provisioned directly (e.g. seeded in the database) by an existing administrator.
When creating a user with an `institution_id`, the institution must already exist or
the request is rejected with `400`.

## Configuration

Copy `backend/.env.example` to `backend/.env` and adjust `DATABASE_URL`, `SECRET_KEY`,
and CORS origins as needed.
