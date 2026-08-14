# Scientific Collaboration Network Analyzer (SCNA)

SCNA is a full-stack research management platform that helps researchers, institutions, reviewers, and administrators manage academic publications, conferences, research projects, collaborations, and citation networks in one place. It was built as part of an Infosys Springboard internship, developed by a five-person team, and deployed as two separate services (a FastAPI backend and a Flask frontend) talking to a shared PostgreSQL database on Supabase.

This document explains what the project does, how the two services fit together, what every module is responsible for, how the database is organized, and how to run and deploy it yourself.

---

## Table of Contents

1. [What This Project Does](#what-this-project-does)
2. [Architecture](#architecture)
3. [Tech Stack](#tech-stack)
4. [User Roles](#user-roles)
5. [Project Structure](#project-structure)
6. [Modules in Detail](#modules-in-detail)
7. [Database Schema](#database-schema)
8. [Authentication & Security](#authentication--security)
9. [Getting Started (Local Development)](#getting-started-local-development)
10. [Running with Docker Compose](#running-with-docker-compose)
11. [Environment Variables](#environment-variables)
12. [Deployment](#deployment)
13. [Known Architectural Notes](#known-architectural-notes)
14. [Team](#team)

---

## What This Project Does

SCNA gives a research institution's staff a single system to:

- Register and log in as a researcher, with optional two-factor login (email OTP) and reCAPTCHA-protected sign-in.
- Build a researcher profile (department, research interests, skills, affiliations) tied to an institution.
- Track **publications** — draft them, attach files, submit them for review, and see them go through a reviewer approval workflow before becoming "published."
- Record **citations** between publications (or to external papers not in the system) and see citation leaderboards and a citation network graph.
- Create and browse **conferences**, register to attend/present, build a session agenda, and upload presentation files.
- Send and accept **collaboration requests** with other researchers, see an auto-computed "collaboration strength" based on shared publications, browse a network graph of who collaborates with whom, and get suggested collaborators.
- Create and manage **research projects** with a lead, an invited team (invite/accept, not auto-add), and a status lifecycle.
- Let **System Admins** manage institutions, assign reviewers (per-institution or per-publication), manage user accounts/roles, and review a full **audit log** of who did what.
- Get **in-app + email notifications** for things like an incoming collaboration request or a review decision.
- Generate and export **reports** (summary stats, publications, projects, collaborations, institutions) as Excel or PDF.

## Architecture

SCNA is two independently deployable services:

```
 ┌───────────────────┐        HTTP (JSON)        ┌────────────────────┐        SQL         ┌──────────────┐
 │   Flask Frontend   │  ───────────────────────▶ │   FastAPI Backend   │ ─────────────────▶ │  PostgreSQL   │
 │  (server-rendered   │ ◀─────────────────────── │   (REST API, JWT)    │ ◀───────────────── │  (Supabase)   │
 │   Jinja2 templates) │                            └────────────────────┘                     └──────────────┘
 └───────────────────┘
        ▲
        │ browser (HTML, session cookie)
        │
     End user
```

- **Backend (`backend/`)** — a FastAPI REST API. It owns all business logic, database access (via SQLAlchemy models + Alembic migrations), JWT issuance/verification, password hashing, email sending, reCAPTCHA verification, and file storage for uploads. It has no UI of its own — everything is JSON over HTTP, and it ships interactive API docs at `/docs`.
- **Frontend (`frontend/`)** — a Flask app that renders all the HTML the user actually sees (Jinja2 templates). It holds no business logic of its own: every page is built by calling the backend's REST API with the `requests` library, using the JWT stored in the user's Flask session as a Bearer token, and rendering the JSON response into a template.
- **Database** — PostgreSQL, hosted on Supabase in production (shared by the whole team) or a local Postgres instance for solo development. Alembic manages every schema change as a versioned migration under `backend/alembic/versions/`.

This split means the backend can be used by any other client too (a mobile app, a different frontend, `curl`, etc.) since it's a normal REST API with its own OpenAPI docs — the Flask app is just the reference client.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend framework | FastAPI (Python) |
| Backend server | Uvicorn (ASGI) |
| ORM | SQLAlchemy 2.0 (typed `Mapped[...]` models) |
| Migrations | Alembic |
| Validation / schemas | Pydantic v2 |
| Auth | JWT (`python-jose`) + bcrypt password hashing (`passlib`) |
| Bot protection | Google reCAPTCHA v2 (checkbox) on login |
| Frontend framework | Flask + Jinja2 templates |
| Frontend ↔ backend | `requests` (Flask calls the FastAPI JSON API) |
| Database | PostgreSQL (Supabase in production) |
| Reports / export | `openpyxl` (Excel), `reportlab` (PDF) |
| Containerization | Docker + Docker Compose |
| Deployment | Render (two services, one per Dockerfile) |
| CI | GitHub Actions (`.github/workflows/docker-build-deploy.yml`) |

## User Roles

Every user has exactly one role, stored on the `users` table:

| Role | Can do |
|---|---|
| **Researcher** | Default role for self-registration. Manages their own profile, publications, citations, conference participation, collaborations, and projects. |
| **Institution Admin** | Everything a Researcher's institution-scoped views need, plus managing their institution's record and (for conferences/projects tied to their institution) organizer-level access. Granted by a System Admin, never self-selected at signup. |
| **Reviewer** | Reviews publications they're assigned to (see [Reviewer Assignments](#reviewer-assignments--publication-review)). Has no reviewing power over anything without an explicit assignment. Granted by a System Admin. |
| **System Admin** | Superuser. Can do everything above, plus manage all user accounts/roles, assign reviewers, view the audit log, and see cross-institution reports. |

Registration (`POST /auth/register`, the public `/register` page) **always** creates a Researcher — the other three roles are only granted by an existing System Admin via the admin user-management screen, never chosen by the person signing up.

## Project Structure

```
InfosysInternship/
├── backend/                      FastAPI REST API
│   ├── app/
│   │   ├── main.py               App factory, router registration, CORS, /health
│   │   ├── core/                 Cross-cutting concerns
│   │   │   ├── config.py         Settings (env vars) via pydantic-settings
│   │   │   ├── security.py       JWT + password hashing
│   │   │   ├── captcha.py        reCAPTCHA v2 server-side verification
│   │   │   ├── email.py          SMTP email sending (best-effort)
│   │   │   ├── notifications.py  In-app notification creation helper
│   │   │   └── audit.py          Audit-log write helper
│   │   ├── db/                   SQLAlchemy session/engine + declarative base
│   │   ├── models/                One file per DB table (SQLAlchemy ORM models)
│   │   ├── schemas/                One file per resource (Pydantic request/response models)
│   │   └── api/routes/            One file per resource (FastAPI routers — the actual endpoints)
│   ├── alembic/versions/          Every schema migration, in order (0001 → 0023+)
│   ├── scripts/create_system_admin.py   Bootstrap a local System Admin account
│   ├── Dockerfile                Runs `alembic upgrade head` then starts uvicorn
│   └── requirements.txt
│
├── frontend/                     Flask server-rendered UI
│   ├── app.py                    Every route: calls the backend API, renders a template
│   ├── templates/                One Jinja2 template per page
│   ├── static/css/style.css
│   ├── Dockerfile
│   └── requirements.txt
│
├── docker-compose.yml            Runs both services + wires them together locally
├── SCHEMA.md                     Early ERD-level schema notes (Milestone 1 snapshot)
├── REQUIREMENTS.md               Original Milestone 1 requirements doc
└── .github/workflows/            CI: Docker build/deploy
```

## Modules in Detail

Each module below maps to a router in `backend/app/api/routes/`, one or more SQLAlchemy models, and one or more Flask routes/templates.

### Authentication & Security
**Backend:** `api/routes/auth.py` · **Models:** `user.py`, `auth_token.py` · **Frontend:** `login.html`, `register.html`, `mfa_verify.html`, `forgot_password.html`, `reset_password.html`, `security_settings.html`

- **Register** (`POST /auth/register`) — creates a `User` (role always `researcher`) with a bcrypt-hashed password, plus an empty `Researcher` profile row so `/researchers/me` works immediately after signup.
- **Login** (`POST /auth/login`) — an OAuth2-password-flow endpoint that also requires a valid reCAPTCHA v2 token. On success it returns a JWT access token (24h expiry by default). If the account has MFA enabled, it instead emails a 6-digit OTP and returns a short-lived `pre_auth_token`.
- **MFA (email OTP)** — `POST /auth/mfa/verify-login` exchanges the OTP + pre-auth token for a real access token. `/auth/mfa/enable` and `/auth/mfa/disable` (from the Security Settings page) toggle it per-user. OTPs are single-use, expire in 10 minutes, and are stored in the shared `auth_tokens` table (`token_type = mfa_otp`).
- **Forgot / Reset Password** — `POST /auth/forgot-password` always returns the same generic response (so it can't be used to check which emails are registered) and, if the account exists, emails a link containing a single-use `password_reset` token (2-hour expiry). `POST /auth/reset-password` consumes that token and sets a new password.
- **JWTs** are verified on every protected endpoint via the `get_current_user` FastAPI dependency (`api/deps.py`), which decodes the token, loads the `User`, and rejects inactive accounts. `require_role(...)` is a dependency factory used to gate admin/reviewer-only endpoints (System Admin is always allowed through as a superuser).
- **reCAPTCHA** verification is fail-closed (a bad/missing token denies login) except when `RECAPTCHA_SECRET_KEY` is left blank, which is treated as "captcha disabled for local dev."

### Researcher Profiles
**Backend:** `api/routes/researchers.py` · **Model:** `researcher.py` · **Frontend:** `profile.html`, `profile_edit.html`, `dashboard.html`

`GET/POST/PUT /researchers/me` let the logged-in user view, create, or update their own profile (department, research interests, skills, affiliations, institution). `GET /researchers/search` powers the "find a collaborator" search box. `GET /researchers/{id}` and its `/publications` and `/conferences` sub-routes expose another researcher's public profile, publication list, and conference history (used on collaboration/project member pages).

### Institution Management
**Backend:** `api/routes/institution.py` · **Model:** `institution.py` · **Frontend:** `institution.html`, `edit_institution.html`

Full CRUD for institutions (name, contact info, address, status), plus `/institutions/mine` (institutions the current user administers) and `/institutions/search/`. Each institution can have an `admin_user_id` — the Institution Admin who manages it — which a System Admin can (re)assign from the edit-institution screen.

### Publications
**Backend:** `api/routes/publications.py` · **Models:** `publication.py` (`Publication`, `PublicationAuthor`) · **Frontend:** `publications.html`, `publication_form.html`, `review_queue.html`, `reviewed_publications.html`

A publication has a title, year, venue, DOI link, abstract, a type (journal paper / conference paper / book / patent / technical report), an uploaded file, a list of co-authors (via `PublicationAuthor`), and a **status**: `draft → submitted → published` (or `archived`). Authors create and edit their own publications and submit them for review, but **cannot self-publish** — only a Reviewer with a matching `ReviewerAssignment` can flip a `submitted` publication to `published` (or send it back to `draft` with a comment) via `PATCH /publications/{id}/review`. `GET /publications/pending-review` and `GET /publications/reviewed-by-me` power the Reviewer's queue and history pages.

### Citations
**Backend:** `api/routes/citations.py` · **Model:** `citation.py`

A citation record links a `citing_publication` (must be in SCNA) to a cited work, which is either **internal** (`cited_publication_id` points at another SCNA publication) or **external** (free-text title/authors/year/venue for a paper outside the system) — enforced by a DB check constraint that exactly one of those is set. Beyond plain CRUD, this module computes:
- `GET /citations/stats/top-papers`, `/top-authors`, `/top-institutions` — citation leaderboards.
- `GET /citations/network` — nodes/edges for the citation graph rendered on the Citation Insights page with `vis-network`.

### Conferences
**Backend:** `api/routes/conferences.py` · **Models:** `conference.py`, `participation.py`, `session.py` · **Frontend:** `conferences.html`, `conference_form.html`, `conference_detail.html`, `conference_history.html`

Conferences belong to an institution and have a type (in-person / virtual / hybrid), dates, and a description. Researchers **register** to attend/present (`ConferenceParticipation`, role: attendee/presenter/organizer/reviewer, status: registered/confirmed/cancelled/attended) and can upload a presentation file once registered. Organizers build a **session agenda** (`ConferenceSession`) with talks that can optionally be linked to a registered presenter. `/conferences/me/history` powers "my conference history."

### Collaborations
**Backend:** `api/routes/collaborations.py` · **Models:** `collaboration.py` (`CollaborationRequest`, `Collaboration`, `CollaborationPublication`) · **Frontend:** `collaborations.html`, `collaboration_detail.html`, `collaboration_network.html`, `suggested_collaborators.html`

This is a two-way handshake model:
1. Researcher A sends a `CollaborationRequest` to Researcher B (`pending`).
2. B accepts, rejects, or A cancels it (`PATCH /collaborations/collaboration-requests/{id}`).
3. Accepting a request creates a durable `Collaboration` edge between the two researchers (`researcher1_id` is always the smaller `researchers.id` of the pair, so "does an edge exist" is a single lookup).
4. A collaboration's **strength** and first/last-collaboration dates are **derived automatically** from publications the two researchers co-author (`recompute_collaboration_metrics`), not hand-entered.

Also included: `GET /collaborations/network` (a graph of the researcher's collaboration neighborhood, depth-configurable) and `GET /collaborations/suggested` (candidate collaborators, e.g. shared institution/interests, who aren't already connected).

### Institution Collaborations
**Model:** `institution_collaboration.py`

A separate, higher-level concept from researcher-to-researcher collaborations above: a formal collaboration *between two institutions* (title, description, status: pending/active/ended, date range). Mirrors the `institution_collaborations` table.

### Projects
**Backend:** `api/routes/projects.py` · **Model:** `project.py` (`Project`, `ProjectMember`) · **Frontend:** `projects.html`, `project_form.html`, `project_detail.html`

A Project is a durable, named body of work — title, description, status (planned/ongoing/completed/cancelled), dates, an owning institution, and a lead researcher. Like Collaborations, team membership is **invite/accept**, not auto-add: `POST /projects/{id}/members` invites a researcher (status `pending`), and `POST /projects/{id}/members/respond` lets them accept or decline. Only `ACCEPTED` members count as real team members (`Project.member_ids`). The lead is auto-added as an `ACCEPTED` `lead` member at creation and never goes through the invite step themselves.

### Reviewer Assignments & Publication Review
**Backend:** `api/routes/reviewer_assignments.py` · **Model:** `reviewer_assignment.py` · **Frontend:** `assign_reviewers.html`

Having the `reviewer` role alone grants **no** reviewing power. A System Admin must grant a `ReviewerAssignment`, scoped **either** to an institution (the reviewer may review any submitted publication whose author belongs to that institution) **or** to one specific publication — never both (DB-enforced). This is what `_is_eligible_reviewer` checks before letting `PATCH /publications/{id}/review` succeed.

### Admin / User Management
**Backend:** `api/routes/admin.py` · **Frontend:** `admin_users.html`

System-Admin-only: `GET /admin/users` lists every user (with role/activity stats aggregated on the frontend for the dashboard), and `PATCH /admin/users/{id}` changes a user's role and/or active status.

### Audit Log
**Backend:** `api/routes/audit.py` · **Model:** `audit_log.py` · **Frontend:** `audit.html`

Every meaningful action across the app (`login`, `login_failed`, `register`, `publication_created`, `publication_reviewed`, `project_deleted`, etc.) is recorded by a single best-effort helper, `log_audit()` (`core/audit.py`) — a logging failure is swallowed so it never breaks the request that triggered it. `GET /audit` (System-Admin-only, paginated, filterable by entity type / action / user / date range) and `GET /audit/actions` (the distinct action list, for the filter dropdown) power the Audit Log page.

### Notifications
**Backend:** `api/routes/notifications.py` · **Model:** `notification.py` · **Frontend:** `notifications.html` + navbar bell

In-app notifications (e.g. "New collaboration request from...", "Your publication was approved") are created by `create_notification()` (`core/notifications.py`) and surfaced via `GET /notifications` (paginated, with unread count), `GET /notifications/unread-count` (cheap navbar badge), `PATCH /notifications/{id}/read`, and `POST /notifications/mark-all-read`.

### Reports & Export
**Backend:** `api/routes/reports.py` · **Frontend:** `reports.html`

Aggregated, role-aware reports — summary stats, publications, projects, collaborations, and (System Admin / Institution Admin only) institutions — each downloadable as **Excel** (`openpyxl`) or **PDF** (`reportlab`) via `/reports/export/{excel|pdf}?type=...`.

## Database Schema

The schema evolved across 23+ Alembic migrations (`backend/alembic/versions/0001_initial.py` through `0023_institution_collaborations.py` and beyond). At a high level:

| Table | Purpose |
|---|---|
| `users` | Login identity: email, password hash, role, active flag, MFA toggle |
| `researchers` | 1:1 extension of a `researcher`-role user: department, interests, skills, affiliations, institution |
| `institutions` | Organizations researchers belong to; has an owning `admin_user_id` |
| `institution_collaborations` | Formal collaborations between two institutions |
| `publications` / `publication_authors` | Papers/books/patents and their (co-)author list |
| `citations` | Citing → cited edges, internal or external |
| `conferences` / `conference_attendances` / `conference_sessions` | Events, who's attending in what role, and the talk agenda |
| `collaboration_requests` / `collaborations` / `collaboration_publications` | The connect-request handshake, the resulting durable edge, and which shared papers back its "strength" |
| `projects` / `project_members` | Research projects and their invite/accept team roster |
| `reviewer_assignments` | Grants a reviewer permission over an institution's or a specific publication's submissions |
| `audit_logs` | Append-only action log |
| `notifications` | Per-user in-app notifications |
| `auth_tokens` | Single-use tokens for password reset and MFA OTPs |

Every table is defined twice, by design: once as a SQLAlchemy model (`backend/app/models/`, the source of truth the running app uses) and once as the Alembic migration(s) that created it (`backend/alembic/versions/`, the source of truth for how to reproduce the schema from scratch).

## Authentication & Security

- Passwords are hashed with **bcrypt** via `passlib`, never stored or logged in plain text.
- Sessions are stateless **JWTs** (HS256, `python-jose`), signed with `JWT_SECRET_KEY` and expiring after `ACCESS_TOKEN_EXPIRE_MINUTES` (24h by default). The frontend stores the token in the signed Flask session cookie, not in browser storage.
- Every protected backend route depends on `get_current_user`, which re-validates the token and re-checks `is_active` on every request — deactivating a user (via the admin panel) takes effect immediately, not just at their next login.
- Role checks are enforced **server-side** in the backend (`require_role(...)`), not just hidden in the frontend UI — the Flask templates hide buttons a user can't use, but the API is the actual gate.
- Login is protected by **reCAPTCHA v2** and optional **email-OTP MFA**.
- Password reset uses single-use, time-boxed tokens and never reveals whether an email is registered.

## Getting Started (Local Development)

### Prerequisites
- Python 3.12+ (backend targets 3.12 in its Dockerfile; a local `python3.14` venv also works)
- A PostgreSQL database (local Postgres, or a free Supabase project)

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows; use `source venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
copy .env.example .env         # then edit .env — see Environment Variables below
```

Make sure the database in `DATABASE_URL` exists, then apply every migration:

```bash
alembic upgrade head
```

Start the API:

```bash
uvicorn app.main:app --reload --port 8000
```

- Health check: http://127.0.0.1:8000/health
- Interactive API docs (Swagger UI): http://127.0.0.1:8000/docs

To create your first admin account locally (rather than manually editing the DB), run:

```bash
python scripts/create_system_admin.py
```

### 2. Frontend

```bash
cd frontend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env         # BACKEND_URL should point at the backend above
python app.py
```

Visit http://127.0.0.1:5000 — start the backend first, since every page the frontend renders depends on it.

## Running with Docker Compose

From the repo root, with `backend/.env` and `frontend/.env` already filled in:

```bash
docker compose up --build
```

This builds and starts both services, waits for the backend's `/health` check to pass before starting the frontend, and runs `alembic upgrade head` automatically inside the backend container on every start (see `backend/Dockerfile`). The frontend is reachable at http://localhost:5000, the backend at http://localhost:8000.

## Environment Variables

### Backend (`backend/.env`)

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string (`postgresql+psycopg://...`) |
| `JWT_SECRET_KEY` | Signing secret for access tokens — must be a long random string in production |
| `JWT_ALGORITHM` | Defaults to `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT lifetime (default 1440 = 24h) |
| `FRONTEND_URL` | Used to build links in outbound emails (e.g. the password-reset link) |
| `SMTP_HOST` / `SMTP_PORT` / `SMTP_USERNAME` / `SMTP_PASSWORD` / `SMTP_USE_TLS` / `SMTP_FROM_EMAIL` / `SMTP_FROM_NAME` | Outbound email config. Leave `SMTP_HOST` blank to run without real email — the app logs a "would have sent" warning instead of failing |
| `RECAPTCHA_SECRET_KEY` | Server-side reCAPTCHA v2 secret. Defaults to Google's public test key |

### Frontend (`frontend/.env`)

| Variable | Purpose |
|---|---|
| `BACKEND_URL` | Base URL of the FastAPI backend |
| `FLASK_SECRET_KEY` | Signs the Flask session cookie — any random string for dev, a real secret in production |
| `RECAPTCHA_SITE_KEY` | Public reCAPTCHA v2 site key, must be the counterpart of the backend's `RECAPTCHA_SECRET_KEY` |

## Deployment

Both services are deployed independently on **Render**, one Web Service per Dockerfile (`backend/Dockerfile`, `frontend/Dockerfile`), with `BACKEND_URL` on the frontend service pointed at the backend's live Render URL. The backend's Dockerfile runs `alembic upgrade head` before starting Uvicorn on every deploy, so the production schema is always brought up to date automatically — and fails the deploy loudly if a migration can't apply, rather than serving against a stale schema.

> **Free-tier note:** Render's free plan spins a service down after ~15 minutes of inactivity; the next request has to "cold start" it (30–60s), which can otherwise be mistaken for a broken deploy. A scheduled ping (e.g. via [cron-job.org](https://cron-job.org)) against the backend's `/health` endpoint every 10 minutes keeps it warm — see `backend/app/main.py` for the `/health` route.

CI (`.github/workflows/docker-build-deploy.yml`) builds both Docker images on push.

## Known Architectural Notes

- **Shared Supabase database.** All five team members and every deployed environment point at the same Postgres instance during development. Several models/migrations (`institution_collaboration.py`, `project.py`, `notification.py`, `auth_token.py`) explicitly document places where a table's real, already-existing shape (created by a parallel migration chain sharing the same DB) was adopted as-is in code rather than fought with a conflicting `ALTER TABLE`. Where this happens, the migration is written idempotently (existence checks, `checkfirst=True`) instead of assuming a clean slate.
- **Institution Admin has no `Researcher` row.** Several frontend routes explicitly branch on this — e.g. the Publications list still needs to load for an Institution Admin even though `researcher_id` is always `None` for them, because the backend independently scopes their view by institution.
- **Reviewers have no default power.** The `reviewer` role is necessary but not sufficient to review anything — a matching `ReviewerAssignment` row is always required (see [Reviewer Assignments](#reviewer-assignments--publication-review)).
- **Collaboration/Project "strength" and team membership are derived, not hand-entered** — see the Collaborations and Projects sections above.

## Team

Built by a five-person team as part of an Infosys Springboard internship:

- Prem Kumar
- Hari Kumar
- Indhu Vadana
- Vishal Kumar
- Eswar Kumar
