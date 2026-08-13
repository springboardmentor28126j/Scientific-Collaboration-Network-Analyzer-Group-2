# Scientific Collaboration Network Analyzer (SCNA)

SCNA is a research-management web application for universities, research institutes, publishers, and funding organisations. It centralises researchers, institutions, publications, conferences, projects, citations, collaborations, reports, and role-based workflows in one platform.

The system does **not** use AI analysis. Its analytics are generated from stored research data using database queries, charts, reports, and collaboration-network visualisation.

## Table of contents

- [Project objective](#project-objective)
- [Key features](#key-features)
- [Roles and access](#roles-and-access)
- [Technology stack](#technology-stack)
- [Architecture](#architecture)
- [Project structure](#project-structure)
- [Installation and local setup](#installation-and-local-setup)
- [Environment configuration](#environment-configuration)
- [Running with Docker](#running-with-docker)
- [Modules and workflows](#modules-and-workflows)
- [Reports and exports](#reports-and-exports)
- [API documentation](#api-documentation)
- [Testing](#testing)
- [Demo walkthrough](#demo-walkthrough)
- [Troubleshooting](#troubleshooting)
- [Known limitations and future work](#known-limitations-and-future-work)

## Project objective

The objective is to build a Scientific Collaboration Network Analyzer that enables academic organisations to:

- manage researchers and institutional affiliations;
- maintain a publication repository with authors, DOI, status, and PDF uploads;
- record conferences, projects, citations, and collaborations;
- visualise research collaboration networks;
- generate institution and publication analytics reports;
- provide secure, role-specific workspaces; and
- notify users about important actions through the application and optional email.

## Key features

- JWT login with bcrypt-hashed passwords, confirmation, and strong-password validation.
- Registration request and administrator approval workflow.
- Researcher, Institution Admin, Publisher, Reviewer, and System Admin roles.
- Account-to-researcher/institution workspace assignment.
- Researcher, institution, publication, conference, project, citation, and collaboration management.
- Publication status workflow: Draft, Submitted, Published, Archived.
- DOI duplicate validation, author assignment, and PDF upload support.
- Interactive collaboration network with search, institution filter, hover effect, and researcher detail panel.
- Collaboration request lifecycle: pending, accepted, rejected.
- Review workflow: reviewer assignment, due date, comments, approve/request-changes/reject decision.
- Role-aware dashboards and backend-enforced data scope.
- Institution reports with analytics charts, downloadable Excel, and server-generated PDF.
- Notifications, unread count, mark-all-read, announcements, and optional Resend email delivery.
- Audit log for important system activity.
- Data-quality checks for incomplete publications/researchers.
- Search, sorting, filtering, and pagination tools for data tables.
- Docker configuration and Swagger/OpenAPI API documentation.

## Roles and access

| Role | Main responsibility | Typical access |
| --- | --- | --- |
| System Admin | Operates the complete platform | All modules, account approval, account assignment, announcements, audit log, data quality, reports |
| Institution Admin | Operates one assigned institution | Institution researchers, publications, projects, conferences, reports, reviewer assignment |
| Researcher | Manages personal academic activity | Assigned profile, own publications/projects/collaborations, conferences, reports |
| Publisher | Manages the publication process | Publication repository, statuses, authors, DOI, citations, reviewer assignment, reports |
| Reviewer | Reviews assigned publications | Assigned review queue, decision, due date, comments, assigned publications |

The frontend hides irrelevant navigation, but access is also checked in the backend. For example, a Reviewer cannot access unassigned publications by typing an API URL directly.

## Technology stack

| Area | Tools |
| --- | --- |
| Backend | Python, FastAPI, Uvicorn |
| Database layer | SQLAlchemy, PostgreSQL/Supabase or local SQLite |
| Authentication | JWT, OAuth2 password bearer flow, Passlib bcrypt |
| Frontend | HTML, CSS, JavaScript, Bootstrap 5, Bootstrap Icons |
| Visualisation | Chart.js and Cytoscape-based collaboration network |
| Email | Resend API (optional) |
| Export | ReportLab PDF, OpenPyXL Excel |
| Deployment | Docker, Docker Compose |
| Testing | Pytest |

## Architecture

```mermaid
flowchart LR
  Browser[Browser frontend] -->|REST API + JWT| FastAPI[FastAPI backend]
  FastAPI --> SQLAlchemy[SQLAlchemy ORM]
  SQLAlchemy --> DB[(PostgreSQL / Supabase or SQLite)]
  FastAPI --> Files[Local PDF uploads]
  FastAPI --> Resend[Resend email API]
  FastAPI --> Exports[PDF and Excel report exports]
```

## Project structure

```text
Scientific-Collaboration-Network-Analyzer-Group-2/
├── app/
│   ├── main.py                 # FastAPI app, routers, static mounts
│   ├── models.py               # SQLAlchemy database models
│   ├── schemas.py              # Pydantic request/response schemas
│   ├── auth.py                 # JWT and password utilities
│   ├── permissions.py          # Role and workspace authorization
│   ├── notification_service.py # In-app/email notification service
│   ├── audit.py                # Audit-log helper
│   └── routes/                 # API modules
├── frontend/
│   ├── pages/                  # Module, dashboard, report, admin pages
│   ├── js/                     # Shared layout and page scripts
│   └── css/                    # Shared styling
├── tests/                      # Automated smoke tests
├── uploads/                    # Uploaded publication PDFs (local development)
├── .env.example                # Safe environment variable template
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Installation and local setup

### Prerequisites

- Python 3.11 or newer
- PostgreSQL/Supabase database **or** SQLite for a simple local demo
- Node.js only if your frontend is served through Vite
- Git (optional, for cloning)

### 1. Clone/open the project

```powershell
git clone <your-repository-url>
cd Scientific-Collaboration-Network-Analyzer-Group-2
```

### 2. Create and activate a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this for the current terminal only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### 3. Install Python packages

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and fill in your own values. Do not commit `.env`.

```powershell
Copy-Item .env.example .env
```

### 5. Start the backend

```powershell
uvicorn app.main:app --reload
```

Backend API: `http://127.0.0.1:8000`

Swagger API documentation: `http://127.0.0.1:8000/docs`
ReDoc: `http://127.0.0.1:8000/redoc`

### 6. Start/open the frontend

If Vite is configured in `frontend/`:

```powershell
cd frontend
npm install
npm run dev
```

Open the URL printed by Vite, commonly `http://localhost:5173`.

For a simple backend-served static demo, open:

```text
http://127.0.0.1:8000/frontend/index.html
```

## Environment configuration

Example `.env` values:

```env
# Use either PostgreSQL/Supabase or leave this absent for local SQLite.
DATABASE_URL=postgresql://username:password@host:5432/database_name

# Use a long random secret in a real deployment.
SECRET_KEY=replace-with-a-long-random-secret
ACCESS_TOKEN_EXPIRE_MINUTES=120
APP_URL=http://localhost:5173

# Optional email delivery through Resend.
RESEND_API_KEY=re_your_resend_api_key
RESEND_FROM_EMAIL=SCNA Notifications <notifications@your-verified-domain.com>
```

Never paste passwords, database URLs, Resend keys, or JWT secrets into GitHub, screenshots, reports, or chat messages. If a secret is exposed, rotate it immediately.

## Running with Docker

Docker runs the FastAPI application on port 8000.

```powershell
docker compose up --build
```

Stop it with:

```powershell
docker compose down
```

`docker-compose.yml` reads variables from `.env`, so configure that file before starting Docker.

## Modules and workflows

### 1. User management and access approval

1. A visitor registers as Researcher, Institution Admin, Publisher, or Reviewer.
   Registration requires a matching confirmation password with at least 8 characters, uppercase, lowercase, number, and special character.
2. Researcher accounts can become active immediately; other role requests remain pending.
3. A System Admin opens **Account Approvals**.
4. The System Admin approves or rejects the request. Rejections require a reason.
5. For Researcher and Institution Admin, the System Admin assigns the relevant researcher profile or institution workspace.
6. The user receives an in-app notification and optionally an email.

System Admin account tools:

- **Account Approvals**: process new role requests.
- **Account Directory**: update researcher/institution assignments for existing users.
- **Audit Log**: review important actions.
- **Data Quality**: find incomplete research data.

### 2. Researcher management

Researcher records include:

- full name;
- email;
- institution;
- department;
- designation;
- skills; and
- research interests.

The researcher dashboard uses the linked researcher profile to show only that account’s records. Institution Admins see researchers belonging to their assigned institution.

### 3. Institution management

System Admins create/edit institutions. Institutions can store name, address, website, and contact email. Institution reports calculate researcher and publication statistics for the selected institution.

### 4. Publication management

Publication records support:

- title and abstract;
- type: journal paper, conference paper, book, patent, technical report, etc.;
- status: Draft, Submitted, Published, Archived;
- DOI duplicate validation;
- publication date and journal/venue;
- institution;
- one or more researcher authors; and
- local PDF upload.

Publisher and authorised institution users can manage the publication workflow. Researchers see only publications connected to their profile. Reviewers see only publications assigned to them for review.

### 5. Projects and conferences

- Create a project with funding agency, status, dates, institution, and researcher assignments.
- Create conference records with date and location.
- Register researcher participation and optional presentation title.
- Institution Admins see their institution scope; Researchers see their assigned records.

### 6. Collaboration management and network

Collaborations can be created between two researchers and optionally linked to a project/publication. Requests move through Pending, Accepted, or Rejected status.

The **Collaboration Network** page visualises co-authorship and accepted collaborations. It includes:

- researcher name labels;
- hover enlargement;
- researcher search/highlighting;
- institution filter;
- collaboration edge weights; and
- a detail drawer with collaborators and shared research activity.

### 7. Citations

A citation links a citing publication to a cited publication. The system prevents a publication from citing itself in the user interface and makes citation counts available in dashboards/reports.

### 8. Reviewer workflow

This makes the Reviewer role a real workflow rather than only a dashboard view.

1. System Admin, Institution Admin, or Publisher opens **Reviews**.
2. Select a publication, active Reviewer account, and optional due date.
3. The Reviewer logs in and opens **Reviews**.
4. The Reviewer sees only assignments made to that account.
5. The Reviewer adds comments and chooses **Approve**, **Request Changes**, or **Reject**.
6. The decision, comment, due date, timestamp, and audit record are saved.

### 9. Notifications and email

Every signed-in user has a notification bell with unread count and Mark All Read support. System Admin can send announcements to selected recipients. If Resend configuration is present, the same announcement may be delivered by email.

Email delivery is optional; in-app notifications still work when Resend is not configured.

### 10. Audit and data quality

The audit log records key actions such as registration, successful/failed/blocked login, logout, denied protected actions, account approval/rejection, announcements, researcher profile changes, publication changes (including author/PDF changes), projects and team assignments, conferences, citations, collaborations, and review decisions. Each record includes date/time, actor, actor role, module, action, description, and client IP address when available.

The Data Quality page helps the System Admin find:

- publications missing a DOI;
- publications without authors;
- researchers without institution;
- researchers missing email; and
- suspended accounts.

## Reports and exports

The Reports module supports a generated-report history for institutions.

1. Select an institution and generate its report.
2. Use **View** from generated report history.
3. The full report displays totals, publication-status-by-year chart, top researchers, and collaboration activity.
4. Download a native `.xlsx` Excel workbook or server-generated `.pdf` report.

Overall analytics support charts for publication trends, publication types, institution comparisons, top researchers, and top collaborators.

## API documentation

FastAPI automatically produces interactive Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

Important API groups:

| API prefix | Purpose |
| --- | --- |
| `/users` | registration, login, approvals, account assignments/status |
| `/researchers` | researcher records |
| `/institutions` | institutions and institution reports |
| `/publications` | publications, authors, upload |
| `/conferences` | conferences and participation |
| `/projects` | projects and researcher assignments |
| `/collaborations` | collaboration requests and network data |
| `/citations` | citation links |
| `/reviews` | reviewer assignment and decisions |
| `/reports` | reports, analytics, PDF/Excel exports |
| `/notifications` | notifications and announcements |
| `/audit-logs` | protected system audit history |
| `/admin/data-quality` | protected data-quality checks |

All protected requests require this header:

```text
Authorization: Bearer <access_token>
```

## Database entities

Core entities include:

- `User` — login, role, account status, researcher/institution workspace link.
- `Researcher` — academic profile and institution affiliation.
- `Institution` — organisation details.
- `Publication` — repository record, status, DOI, authors, PDF path.
- `Conference` and `ConferenceParticipation` — events and participation.
- `Project` and `ProjectAssignment` — research projects and teams.
- `Collaboration` — researcher relationships and request status.
- `Citation` — linked publications.
- `ReviewAssignment` — reviewer, due date, comment, decision, timestamp.
- `GeneratedReport` — generated institution-report history.
- `Notification` — user notifications and email-delivery state.
- `AuditLog` — important activity history.

## Testing

Run tests after activating the virtual environment:

```powershell
pytest -q
```

The included smoke tests verify key security assumptions. Before final submission, manually test the role workflows in the next section as well.

## Demo walkthrough

Use this order for your Friday presentation:

1. **Login as System Admin** — show Admin Dashboard, notification bell, sidebar, Account Approvals, Account Directory, Audit Log, and Data Quality.
2. **Researcher module** — show profile fields, researcher list, and linked personal dashboard scope.
3. **Publication module** — create/open a publication, assign authors, show statuses and DOI/PDF fields.
4. **Collaboration module** — create a request, show pending/accepted status, then open Collaboration Network.
5. **Projects and conferences** — show project assignment and conference participation.
6. **Citations** — show link between two publications.
7. **Reports** — generate institution report, open charts, download Excel/PDF.
8. **Reviewer workflow** — as Publisher/Admin assign a Reviewer; sign in as Reviewer; add comments and submit a decision.
9. **Notifications/Audit** — show that a major action appears in the notification system and audit log.

For a one-page speaking guide, see [docs/PRESENTATION_GUIDE.md](docs/PRESENTATION_GUIDE.md).

## Troubleshooting

### Backend fails to start with a database connection error

- Confirm your `DATABASE_URL` in `.env` is correct.
- For Supabase, use the Session Pooler connection string if direct connections fail on your network.
- Confirm the Supabase project is running and the database password is current.
- Never display the connection string in a screenshot.

### `Unable to load recipients` or missing protected data

- Sign out and sign in again to get a fresh JWT token.
- Confirm you are using a System Admin account for admin-only pages.
- Confirm backend is running on port 8000.

### A role dashboard shows no personal data

- Login as System Admin.
- Open **Account Directory**.
- Assign the user to the correct researcher profile or institution.
- Sign out and sign in again as that user.

### Email announcement is not sent

- In-app notifications still work without email configuration.
- Configure `RESEND_API_KEY` and verify the `RESEND_FROM_EMAIL` sender/domain in Resend.

### Frontend does not show recent updates

- Restart the backend after Python changes.
- Hard refresh the browser using `Ctrl + F5`.
- Restart the Vite frontend server if applicable.

## Known limitations and future work

This is a classroom project with a professional workflow foundation. Future production improvements would include:

- versioned Alembic migrations instead of compatibility startup migrations;
- a larger automated API/UI test suite;
- password reset and email verification;
- cloud object storage for publication uploads;
- background jobs and email-delivery webhooks;
- richer reviewer discussion threads and attachments;
- real database backup/restore administration;
- production CORS origins and environment-specific frontend API URL;
- CI/CD pipeline and hosted deployment.

## Security notes

- Passwords are stored as bcrypt hashes.
- Protected endpoints use JWT authentication.
- Role checks are enforced in backend routes.
- Workspace scope limits researcher/institution data visibility.
- `.env` is ignored by Git; only `.env.example` should be committed.

## License

This project is developed for academic use by Group 2.
