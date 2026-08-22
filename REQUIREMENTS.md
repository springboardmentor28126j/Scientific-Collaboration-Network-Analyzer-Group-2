# Scientific Collaboration Network Analyzer — Milestone 1 Requirements

## 1. Scope of Milestone 1
Per project doc (Section 5, Milestone 1, Week 1-2):
- Requirement gathering
- Database schema
- Backend setup (FastAPI)
- Frontend setup (Flask — confirmed with mentor/user, overrides the doc's Milestone-1 line
  which said "React setup"; Tech Stack section 7 lists Tkinter/PyQt/Flask, not React)
- Authentication (JWT)
- Researcher profiles

**Milestone 1 exit outcomes (per doc):**
- Authentication completed
- User management functional
- Researcher module completed

## 2. Roles (Module 1 — User Management)
- Researcher
- Institution Admin
- Reviewer
- System Admin

All four roles exist as a `role` field on the User entity from day one, but only
Researcher + basic admin flows are exercised in Milestone 1. Reviewer/System Admin
UI comes with later milestones (Collaboration, Audit).

## 3. Core Entities Needed for Milestone 1

### User
- id, email (unique), password_hash, role, is_active, created_at

### Institution
- id, name, address, created_at
(Full "Institution Management" workflows expand in later milestones; Milestone 1
only needs enough to let a Researcher be affiliated with one.)

### Researcher (extends User via 1:1 relation)
- id, user_id (FK -> User), institution_id (FK -> Institution, nullable),
  department, research_interests (text), skills (text), affiliations (text)

## 4. Milestone 1 Features (mapped from Module 1 & 2 of the doc)

### Module 1 — User Management
- Registration (email + password, role defaults to "researcher" for self-signup)
- Login (JWT access token)
- Researcher Profile (create/view/update, tied 1:1 to a User)
- Institution Management (minimal: create/list institutions, so a researcher can
  select one during profile setup)

### Module 2 — Researcher Management
- Academic profile fields: department, research interests, skills, affiliations
- Profile is editable by the owning researcher after login

## 5. Out of Scope for Milestone 1
Publication, Collaboration, Conference, Citation, Reports, Audit modules — these
belong to Milestones 2 and 3 per the doc's own week-wise timeline.

## 6. Tech Stack for Milestone 1 (per Section 7, as clarified with user)
- Backend: Python 3, FastAPI, SQLAlchemy, Alembic, Pydantic, Uvicorn
- Frontend: Flask (server-rendered templates), requests (to call the FastAPI API)
- Database: PostgreSQL (Milestone 1 dev default: SQLite fallback documented in
  backend/README so the user can run it without installing Postgres immediately)
- Auth: JWT (python-jose) + password hashing (passlib/bcrypt)
