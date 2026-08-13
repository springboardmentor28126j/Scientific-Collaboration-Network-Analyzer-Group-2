# ResearchMesh — Scientific Collaboration & Research Management System

ResearchMesh is a full-stack research management platform designed to manage the lifecycle of academic research, from institution and user onboarding through publication management, peer review, references, dashboards, notifications, and publication discovery.

The project is implemented as a production-oriented FastAPI + PostgreSQL backend and a React + TypeScript frontend, with Docker-based local development, Alembic migrations, automated tests, Cloudinary file storage, and email-based account workflows.

## Live Application

**Frontend:**  
https://researchmesh-frontend.onrender.com/

> The URL above is the team's deployed frontend. Backend deployment/API availability depends on the current Render configuration.

---

## Core Capabilities

### Authentication & Account Lifecycle

- JWT access and refresh-token authentication
- OAuth2 password-flow-compatible login
- Role-based access control
- Secure password hashing
- Email verification
- Invitation-based verification for researchers and reviewers
- Forgot-password workflow
- Password reset workflow
- Protected routes
- Account activation/deactivation
- Institution-level access control
- Automatic Super Admin bootstrap

### Supported Roles

| Role | Purpose |
|---|---|
| `SUPER_ADMIN` | Platform-wide administration |
| `INSTITUTION_ADMIN` | Manages an institution and its users |
| `RESEARCHER` | Creates and manages research publications |
| `REVIEWER` | Reviews assigned publications |

---

## Institution Management

Institutions can register themselves with:

- Institution name
- Address
- Logo
- Initial administrator details

Institution administration includes:

- Institution listing
- Institution activation/deactivation
- Institution-specific users
- Researcher management
- Reviewer management
- Institution-scoped authorization

Institution logos are designed to use Cloudinary for cloud storage.

---

## User Management

Institution administrators can manage researchers and reviewers within their own institution.

Supported functionality includes:

- Create researcher accounts
- Create reviewer accounts
- Invite users through email
- Verify invited accounts
- Activate/deactivate users
- Search researchers
- Search reviewers
- View current user profile
- Role-aware access control

Researchers and reviewers cannot access institution-admin-only operations.

---

## Publication Management

ResearchMesh supports the publication lifecycle:

```text
DRAFT
  ↓
SUBMITTED
  ↓
UNDER_REVIEW
  ↓
REVISION_REQUIRED
  ↓
ACCEPTED / REJECTED
  ↓
PUBLISHED
  ↓
ARCHIVED
```

Publication functionality includes:

- Create publications
- View publication details
- Update publications
- Delete publications where permitted
- Submit publications for review
- Editorial decisions
- Publish publications
- Archive publications
- Publication history
- Publication versioning
- PDF upload and storage
- Secure PDF download
- DOI support
- Publication type classification
- Institution association

Supported publication types include:

- Journal
- Conference
- Book
- Patent
- Technical Report

---

## Publication Authors

A publication can contain multiple authors with:

- Author ordering
- Corresponding-author support
- Co-author management
- Researcher association

---

## Conference Publications

Conference-specific metadata is supported, including:

- Conference name
- Venue
- City
- Country
- Publication date
- Proceedings
- ISBN
- ISSN
- Publisher
- Conference outcome

---

## Peer Review

The platform includes a reviewer workflow.

Capabilities include:

- Assign reviewers to publications
- View assignments
- Reviewer-specific dashboard
- View publication reviews
- Submit/manage review information
- Editorial decisions

Supported recommendations include:

- Accept
- Minor Revision
- Major Revision
- Reject

---

## Publication References & Citations

Publications support reference management.

Researchers can:

- Add references
- View references
- Update references
- Delete references
- Maintain reference ordering

Reference metadata includes:

- Title
- Authors
- Publication name
- DOI
- URL
- Publication year

---

## Publication Catalog

The platform includes a publication discovery/catalog experience.

Features include:

- Browse published publications
- Browse archived publications
- Search publications
- Sort results
- Filter by publication type
- Pagination
- Publication detail pages
- PDF download for permitted users

---

## Dashboards & Analytics

Dashboards are role-aware.

### Super Admin Dashboard

- Total publications
- Publication status distribution
- Institution count
- Researcher count
- Reviewer count
- Researcher leaderboard

### Institution Admin Dashboard

- Institution publication statistics
- Researchers
- Reviewers
- Institution-level research activity

### Researcher Dashboard

- Own publications
- Co-authored publications
- Publication status overview

### Reviewer Dashboard

- Assigned reviews
- Pending reviews
- Completed reviews

The frontend also includes publication-status visualizations and dashboard cards.

---

## Notifications

The backend includes a notification system for events such as:

- Co-author added
- Publication published
- Review assigned
- Conference created

Notifications support:

- Unread count
- Mark notification as read
- Mark all notifications as read

---

## Frontend

The frontend is a React + TypeScript application built with Vite.

### Main application areas

```text
Login
Register Institution
Forgot Password
Reset Password
Verify Email
Verify Invite

Dashboard
Profile
Institutions
Users
Researcher
Publications
Publication Details
Reviewer
Publication Catalog
Catalog Details
```

### Frontend technologies

- React
- TypeScript
- Vite
- React Router
- Tailwind CSS
- Radix UI
- shadcn-style UI components
- React Hook Form
- Zod
- Zustand
- Recharts
- Lucide Icons
- Vitest

The frontend includes reusable components for:

- Authentication layouts
- Dashboard layouts
- Protected routes
- Forms
- Dialogs
- Tables
- Cards
- Charts
- Notifications
- Image uploads
- Publication creation and references

---

## Backend Architecture

The backend follows a layered FastAPI architecture:

```text
app/
├── api/
│   ├── deps.py
│   └── v1/
│       ├── auth.py
│       ├── dashboard.py
│       ├── institutions.py
│       ├── institution_users.py
│       ├── users.py
│       ├── publications.py
│       ├── publication_conference.py
│       ├── publication_history.py
│       ├── review_assignments.py
│       ├── reviews.py
│       └── notifications.py
│
├── core/
│   ├── config.py
│   ├── dependencies.py
│   ├── exceptions.py
│   ├── security.py
│   └── validators.py
│
├── db/
│   ├── base.py
│   ├── session.py
│   └── init_db.py
│
├── models/
├── repositories/
├── schemas/
├── services/
├── middleware/
└── main.py
```

### Why this architecture?

- **Models** represent database entities.
- **Schemas** define API request/response contracts.
- **Repositories** isolate database operations.
- **Services** contain business logic and orchestration.
- **API routers** expose versioned REST endpoints.
- **Dependencies** implement authentication and authorization.
- **Core** contains security, configuration, validation, and application-level exceptions.

API versioning is provided through:

```text
/api/v1
```

---

## Database

### Database

PostgreSQL

### ORM

SQLAlchemy 2.0 with asynchronous database access through `asyncpg`.

### Migrations

Alembic is used for database schema migrations.

Major entities currently represented include:

```text
users
institutions
publications
publication_authors
publication_conferences
publication_history
publication_versions
publication_references
reviews
review_assignments
notifications
tokens
```

The repository also contains migration history for the initial schema and subsequent publication/reference/notification/institution changes.

---

## Authentication Flow

### Institution registration

```text
Institution Registration
        ↓
Institution + Admin Created
        ↓
Verification Email
        ↓
Email Verification
        ↓
Account Activated
        ↓
Login
        ↓
Access + Refresh Tokens
```

### Researcher / Reviewer onboarding

```text
Institution Admin
        ↓
Creates User
        ↓
Invitation Email
        ↓
User Verifies Invite + Sets Password
        ↓
Account Activated
        ↓
Login
```

### Password reset

```text
Forgot Password
        ↓
Reset Email
        ↓
Single-use Reset Token
        ↓
New Password
        ↓
Login
```

---

## API Overview

The FastAPI application exposes versioned REST APIs under `/api/v1`.

### Authentication

```text
POST /api/v1/auth/login
POST /api/v1/auth/refresh
GET  /api/v1/auth/me
POST /api/v1/auth/verify-email
POST /api/v1/auth/verify-invite
POST /api/v1/auth/forgot-password
POST /api/v1/auth/reset-password
```

### Institutions

```text
POST  /api/v1/institutions/register
GET   /api/v1/institutions
PATCH /api/v1/institutions/{institution_id}/activate
PATCH /api/v1/institutions/{institution_id}/deactivate
```

### Users

```text
GET /api/v1/users/researchers
GET /api/v1/users/reviewers
```

### Publications

The publication API supports:

```text
GET    /api/v1/publications/catalog
GET    /api/v1/publications/catalog/search
GET    /api/v1/publications/catalog/{publication_id}

GET    /api/v1/publications/{publication_id}
PUT    /api/v1/publications/{publication_id}
DELETE /api/v1/publications/{publication_id}

POST   /api/v1/publications/{publication_id}/authors
GET    /api/v1/publications/{publication_id}/authors
DELETE /api/v1/publications/{publication_id}/authors/{researcher_id}

POST   /api/v1/publications/{publication_id}/submit
GET    /api/v1/publications/{publication_id}/download

POST   /api/v1/publications/{publication_id}/decision
PATCH  /api/v1/publications/{publication_id}/publish
PATCH  /api/v1/publications/{publication_id}/archive

POST   /api/v1/publications/{publication_id}/references
GET    /api/v1/publications/{publication_id}/references
PUT    /api/v1/publications/{publication_id}/references/{reference_id}
DELETE /api/v1/publications/{publication_id}/references/{reference_id}
```

### Conference metadata

```text
POST  /api/v1/publication-conference/publications/{publication_id}/conference
GET   /api/v1/publication-conference/publications/{publication_id}/conference
PATCH /api/v1/publication-conference/publications/{publication_id}/conference
```

### Reviews

```text
POST /api/v1/review-assignments/publications/{publication_id}
GET  /api/v1/review-assignments/publication/{publication_id}
GET  /api/v1/review-assignments/my

GET /api/v1/reviews/{review_id}
GET /api/v1/reviews/publication/{publication_id}
```

### Publication history

```text
GET /api/v1/publication-history/{publication_id}/history
```

### Notifications

```text
GET   /api/v1/notifications/unread-count
PATCH /api/v1/notifications/{notification_id}/read
PATCH /api/v1/notifications/read-all
```

### Dashboard

```text
GET /api/v1/dashboard
```

---

## Technology Stack

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- Radix UI
- React Hook Form
- Zod
- Zustand
- Recharts
- Vitest

### Backend

- Python 3.12+
- FastAPI
- Uvicorn
- Pydantic v2
- Pydantic Settings
- SQLAlchemy 2.0 Async
- asyncpg
- Alembic
- python-jose
- Passlib / bcrypt
- python-multipart
- fastapi-mail
- Jinja2

### Infrastructure & Services

- PostgreSQL
- Docker
- Docker Compose
- Cloudinary
- MailCatcher for development email
- Render for deployment
- `uv` for Python dependency management
- pnpm/npm for frontend development

---

## Project Structure

```text
Scientific-Collaboration-Network-Analyzer-Group-2/
│
├── 01_frontend/
│   └── app/
│       ├── public/
│       ├── src/
│       │   ├── api/
│       │   ├── components/
│       │   ├── contexts/
│       │   ├── data/
│       │   ├── hooks/
│       │   ├── pages/
│       │   ├── providers/
│       │   ├── stores/
│       │   └── types/
│       ├── package.json
│       ├── vite.config.ts
│       └── Dockerfile
│
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── middleware/
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   ├── services/
│   └── main.py
│
├── alembic/
│   ├── versions/
│   └── env.py
│
├── docs/
│   ├── architecture.md
│   ├── er_diagram.pdf
│   └── er_diagram.png
│
├── scripts/
├── tests/
├── .env.example
├── docker-compose.yml
├── docker-compose.test.yml
├── Dockerfile
├── Makefile
├── pyproject.toml
├── uv.lock
└── README.md
```

> The repository also contains an older `backend/` directory from an earlier implementation. The production-oriented application used by the current system is the `app/` package described above.

---

## Local Development

### Prerequisites

Install:

- Git
- Docker Desktop
- Docker Compose
- Node.js 20+
- pnpm or npm
- Python 3.12+
- `uv` if running the backend outside Docker

---

## Backend with Docker

Clone the repository:

```bash
git clone <repository-url>
cd Scientific-Collaboration-Network-Analyzer-Group-2
```

Create your environment file:

```bash
cp .env.example .env
```

Configure the required environment variables.

Start the application:

```bash
docker compose up --build
```

The backend will be available at:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

Health check:

```text
http://localhost:8000/health
```

---

## Frontend

Move into the frontend application:

```bash
cd 01_frontend/app
```

Install dependencies:

```bash
pnpm install
```

or:

```bash
npm install
```

Create the frontend environment file:

```text
VITE_API_BASE_URL=http://localhost:8000
```

Start the development server:

```bash
pnpm dev
```

or:

```bash
npm run dev
```

The Vite development server normally runs at:

```text
http://localhost:5173
```

---

## Backend Without Docker

Install dependencies using `uv`:

```bash
uv sync --extra dev
```

Activate the virtual environment if desired:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run migrations:

```bash
alembic upgrade head
```

Start FastAPI:

```bash
uvicorn app.main:app --reload
```

A PostgreSQL instance and SMTP service are required when running outside Docker.

---

## Database Migrations

Create a migration:

```bash
alembic revision --autogenerate -m "describe the change"
```

Apply migrations:

```bash
alembic upgrade head
```

Rollback one migration:

```bash
alembic downgrade -1
```

Always review autogenerated migrations before applying them.

---

## Development Email

Docker Compose includes MailCatcher.

SMTP:

```text
localhost:1025
```

Web interface:

```text
http://localhost:1080
```

Verification, invitation, and password-reset emails can therefore be inspected during development without sending real emails.

---

## Testing

The project uses:

- pytest
- pytest-asyncio
- httpx
- pytest-cov

Run tests:

```bash
pytest
```

Run with coverage:

```bash
uv run pytest --cov=app
```

The repository includes tests covering authentication, institution management, institution users, verification flows, password reset, authorization, and account activation/deactivation.

A separate Docker Compose test environment is provided through:

```text
docker-compose.test.yml
```

---

## Frontend Quality Checks

From:

```bash
cd 01_frontend/app
```

Run TypeScript checking:

```bash
pnpm run check
```

Run linting:

```bash
pnpm run lint
```

Build the production frontend:

```bash
pnpm run build
```

Run frontend tests:

```bash
pnpm run test
```

Preview the production build:

```bash
pnpm run preview
```

---

## Environment Variables

Never commit `.env` files or production credentials.

The repository provides:

```text
.env.example
01_frontend/app/.env.example
```

Important backend configuration includes:

```text
DATABASE_URL
SECRET_KEY
SUPERUSER_EMAIL
SUPERUSER_PASSWORD
CLOUDINARY_CLOUD_NAME
CLOUDINARY_API_KEY
CLOUDINARY_API_SECRET
MAIL_USERNAME
MAIL_PASSWORD
MAIL_FROM
MAIL_SERVER
MAIL_PORT
FRONTEND_URL
BACKEND_CORS_ORIGINS
```

Frontend configuration:

```text
VITE_API_BASE_URL
```

Use strong production secrets and production SMTP credentials when deploying.

---

## Deployment

The backend is designed for Docker-based deployment on Render with:

- Render Web Service
- Render Managed PostgreSQL
- Environment variables configured in Render
- Alembic migrations executed before deployment

The frontend is a Vite application and is deployed separately.

Current frontend deployment:

**https://researchmesh-frontend.onrender.com/**

For production deployment, configure the frontend's:

```text
VITE_API_BASE_URL
```

to point to the deployed backend API.

---

## Security Considerations

The platform includes several security-oriented controls:

- JWT-based authentication
- Access and refresh tokens
- Password hashing
- Password-strength validation
- Email verification
- Single-use verification/reset tokens
- Role-based authorization
- Institution-scoped authorization
- Protected frontend routes
- Account activation/deactivation
- Institution-level access lockout
- Environment-based secrets
- Cloudinary-backed file storage
- Generic forgot-password responses to reduce account enumeration

Production deployments should additionally use:

- HTTPS
- Strong randomly generated secrets
- Secure production SMTP
- Restricted CORS origins
- Secure token storage
- Proper Cloudinary access controls
- Database backups
- Secret management through the deployment platform

---

## Development Workflow

For team development:

```bash
git fetch origin
git checkout <your-branch>
git merge origin/<shared-or-teammate-branch>
```

Before pushing:

```bash
git status
git add .
git commit -m "Describe the change"
git push origin <your-branch>
```

Avoid committing:

```text
.env
node_modules/
.venv/
__pycache__/
dist/
build/
coverage/
```

---

## Documentation

Additional project documentation is available in:

```text
docs/
```

including:

- `architecture.md`
- `er_diagram.pdf`
- `er_diagram.png`

FastAPI also provides automatically generated API documentation through:

```text
/docs
/redoc
```

---

## Project Status

The current repository represents a substantially implemented research management platform covering the major application areas developed through the project's milestone work:

- Authentication & authorization
- Institution management
- User and researcher/reviewer management
- Publication management
- Publication authors
- Conference publication metadata
- Peer review
- Publication history/versioning
- References
- Publication catalog/search
- Role-based dashboards
- Notifications
- Frontend application and protected routes
- Dockerized development
- Database migrations
- Automated testing
- Render deployment

The system is structured so additional capabilities such as richer citation analytics, recommendation systems, ORCID integration, Google Scholar integration, and advanced collaboration analytics can be added without replacing the core architecture.

---

## License

This project was developed as an academic research-management platform and may be extended for institutional or enterprise research workflows.
