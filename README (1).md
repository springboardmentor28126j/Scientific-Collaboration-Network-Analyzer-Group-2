# Scientific Collaboration Network Analyzer

A full-stack platform that helps researchers, institutions, and administrators track publications, conferences, citations, collaborations, and inter-institutional research activity — with built-in reporting, real-time notifications, AI-powered research recommendations, CAPTCHA-protected login, and a full audit trail.

Built as part of the **Infosys Springboard Internship** program.

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Setup](#project-setup)
- [Module Workflows](#module-workflows)
- [Security Features](#security-features)
- [AI-Powered Research Recommendations](#ai-powered-research-recommendations)
- [API Usage](#api-usage)
- [Role Permissions](#role-permissions)
- [Security](#security)
- [Folder Structure](#folder-structure)

---

## Overview

The Scientific Collaboration Network Analyzer gives researchers and institutions a single place to:

- Manage publications, conferences, and citations
- Track cross-institutional research collaborations
- Generate visual reports with PDF/Excel export
- Receive real-time notifications on new activity
- Get **AI-powered research paper recommendations** based on keyword search, with similarity match percentage
- Log in securely with **image-based CAPTCHA verification**
- Maintain a full audit log of system actions for security and compliance

The system supports three distinct roles — **Researcher**, **Institution Admin**, and **System Admin** — each with a tailored dashboard and permission set.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | FastAPI, SQLAlchemy ORM, Pydantic |
| **Frontend** | Flask, Jinja2 (server-rendered templates) |
| **Database** | PostgreSQL (hosted on Supabase) |
| **Authentication** | JWT (JSON Web Tokens) with bcrypt password hashing |
| **CAPTCHA** | Custom image-based CAPTCHA (Pillow) with session verification |
| **AI / Recommendations** | scikit-learn (TF-IDF Vectorizer + Cosine Similarity) |
| **Reporting** | ReportLab (PDF export), openpyxl (Excel export), Chart.js (in-app charts) |
| **Dev Server** | Uvicorn (backend), Flask dev server (frontend) |

---

## Architecture

```
┌─────────────┐        HTTP/JSON        ┌──────────────┐        SQL        ┌──────────────┐
│   Frontend  │ ───────────────────────▶│   Backend    │──────────────────▶│  PostgreSQL  │
│ Flask+Jinja2│◀─────────────────────── │   FastAPI    │◀────────────────── │  (Supabase)  │
│ Port: 5000  │                          │ Port: 8000   │                    │              │
└─────────────┘                          └──────────────┘                    └──────────────┘
```

- The **frontend** (Flask) renders all pages server-side and calls the backend API via `requests`.
- The **backend** (FastAPI) exposes REST endpoints under versioned resource prefixes (`/publications`, `/citations`, `/collaborations`, etc.), each with its own router, model, and schema.
- All backend routers are registered centrally in `backend/app/main.py`.
- The **database** is PostgreSQL, hosted on Supabase, accessed through SQLAlchemy models.
- **CAPTCHA generation** and **AI-based recommendation matching** happen entirely on the frontend (Flask) layer, reusing existing backend APIs — no additional backend endpoints were required.

---

## Project Setup

### Prerequisites

- Python 3.10+
- A Supabase project (or any PostgreSQL instance)
- pip / venv

### 1. Clone the repository

```bash
git clone https://github.com/springboardmentor28126j/Scientific-Collaboration-Network-Analyzer-Group-2.git
cd Scientific-Collaboration-Network-Analyzer-Group-2
```

### 2. Backend setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

Create a `.env` file in `backend/` (see `.env.example`) with your database connection string and secret key.

Run the backend:

```bash
python -m uvicorn app.main:app --reload
```

Backend runs at `http://127.0.0.1:8000`. Interactive API docs available at `http://127.0.0.1:8000/docs`.

### 3. Frontend setup

```bash
cd frontend
pip install -r requirements.txt
python app.py
```

Frontend runs at `http://127.0.0.1:5000`.

The frontend `requirements.txt` now also includes:
```
Pillow
scikit-learn
```

### 4. Access the app

Open `http://127.0.0.1:5000` in your browser, register an account, and log in (you'll be asked to solve a CAPTCHA on the login page).

---

## Module Workflows

| Module | Description |
|---|---|
| **Authentication** | Register/login with email + password; JWT issued on login and stored in session; login is protected by an image-based CAPTCHA |
| **Profile** | Researchers complete their profile (name, department, institution, interests, skills) |
| **Publications** | Create, view, edit, delete publications; upload supporting files; track citation counts |
| **Find Papers (AI Recommendations)** | Search publications by keyword; results are ranked by AI-computed similarity percentage |
| **Conferences** | Add conferences with location and date range; sortable, paginated list |
| **Citations** | Link citing/cited publications with APA, IEEE, or BibTeX formatting; search, filter, sort, paginate |
| **Institutions** | Manage partner institutions (name, type, location, website) |
| **Collaborations** | Track joint projects between two institutions; auto-generates a notification on creation |
| **Reports** | Publication, research, collaboration, and institution reports with charts; export to PDF/Excel |
| **Notifications** | Automatically created when a publication or collaboration is added; unread-count badge |
| **Audit Logs** | Every create/update/delete action across modules is logged with user, action, details, and timestamp |
| **Dashboards** | Role-specific: Researcher (publications/conferences/collaborations), Institution Admin (departments/publications/collaborations, filtered to their institution), System Admin (system-wide view) |

---

## Security Features

### Login CAPTCHA

The login page generates a random 5-character alphanumeric code, renders it as a distorted image (using Pillow), and stores the correct value in the user's session. The user must type the code shown in the image before their credentials are checked.

- Route `/captcha-image` generates and streams the CAPTCHA image on demand.
- The image can be refreshed without reloading the page if it's hard to read.
- On login submission, the typed value is compared (case-insensitive) against the session-stored value before the email/password check proceeds.
- This adds a lightweight, dependency-free layer of bot protection without relying on any third-party service.

---

## AI-Powered Research Recommendations

Accessible from the **"Find Papers"** link in the sidebar (`/recommend`).

**How it works:**

1. The user enters a search query (e.g. `"machine learning privacy"`).
2. The frontend fetches all publications from the existing `GET /publications/` backend API.
3. Each publication's title, type, and DOI are combined into a text document.
4. All publication documents plus the user's query are vectorized using **TF-IDF** (`TfidfVectorizer` from scikit-learn).
5. **Cosine similarity** is computed between the query vector and every publication vector.
6. Each publication is annotated with a `match_percentage` (0–100%).
7. Results are sorted by match percentage (highest first) and the top 10 are displayed.

No external AI API or key is required — the matching is done entirely with classic NLP techniques (TF-IDF + cosine similarity), making it fast, free, and fully self-contained.

---

## API Usage

The backend exposes a REST API under `http://127.0.0.1:8000`. Full interactive documentation (Swagger UI) is available at:

```
http://127.0.0.1:8000/docs
```

### Common patterns

All list endpoints (`GET /publications/`, `/citations/`, `/conferences/`, `/institutions/`, `/collaborations/`, `/audit/logs`) support:

```
?page=1&limit=10&sort_by=<field>&order=asc|desc
```

> **Note:** `limit` is capped at a maximum of **100** by the backend. Requests with a higher limit will return a `422 Unprocessable Entity` error.

and return a paginated envelope:

```json
{
  "total": 42,
  "page": 1,
  "limit": 10,
  "total_pages": 5,
  "publications": [ ... ]
}
```

### Example: create a publication

```bash
curl -X POST http://127.0.0.1:8000/publications/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Federated Learning for Privacy-Preserving AI",
    "type": "journal_paper",
    "doi": "10.1111/fedlearn.2026",
    "author_id": 1
  }'
```

### Example: get audit logs filtered by action

```bash
curl "http://127.0.0.1:8000/audit/logs?action=delete&sort_by=timestamp&order=desc"
```

---

## Role Permissions

| Feature | Researcher | Institution Admin | System Admin |
|---|:---:|:---:|:---:|
| View/manage own publications | ✅ | ✅ | ✅ |
| View/manage own profile | ✅ | ✅ | ✅ |
| View institution-wide publications | ❌ | ✅ (own institution only) | ✅ (all) |
| View institution-wide collaborations | ❌ | ✅ (own institution only) | ✅ (all) |
| Manage institutions | ✅ | ✅ | ✅ |
| Manage conferences, citations, collaborations | ✅ | ✅ | ✅ |
| View reports | ✅ | ✅ | ✅ |
| View audit logs | ✅ | ✅ | ✅ |
| Use AI research recommendations | ✅ | ✅ | ✅ |
| System-wide analytics | ❌ | ❌ | ✅ |

Role is assigned at registration and stored in the session after login. The Institution Admin dashboard additionally requires a one-time institution selection, after which all dashboard metrics are filtered to that institution only.

---

## Security

- **CAPTCHA Verification** — Login requires solving an image-based CAPTCHA before credentials are checked, protecting against automated login attempts.
- **JWT Authentication** — Login issues a JSON Web Token; the token is stored server-side in the Flask session and sent as a Bearer token on authenticated backend requests.
- **Password Hashing** — Passwords are hashed with bcrypt before storage; plaintext passwords are never persisted.
- **Role-Based Access Control** — Every user has one of three roles (Researcher, Institution Admin, System Admin), which determines dashboard content and data visibility.
- **Session Protection** — All sensitive routes check for a valid session token and redirect unauthenticated users to the login page.
- **Audit Logging** — Every create, update, and delete action across Publications, Citations, Conferences, Institutions, and Collaborations is recorded in the `audit_logs` table with the acting user, action type, details, and timestamp — viewable and searchable from the Audit Logs page.
- **Data Isolation** — Institution Admin dashboards only surface data belonging to their own institution, preventing cross-institution data leakage.

---

## Folder Structure

```
scientific-collab-analyzer/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy models (one per resource)
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── routers/         # FastAPI routers (one per resource)
│   │   ├── database.py      # DB connection/session setup
│   │   └── main.py          # App entrypoint, router registration
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── templates/           # Jinja2 HTML templates (includes recommend.html)
│   ├── static/               # CSS
│   ├── app.py                # Flask routes (includes CAPTCHA + recommendation logic)
│   └── requirements.txt      # Now includes Pillow, scikit-learn
│
└── README.md
```

---

## Contributors

Developed as part of the Infosys Springboard Internship — Scientific Collaboration Network Analyzer, Group 2.

**Branch maintained by:** Nandini Ahire (`Nandini_Ahire`)

**Added in this update:** Login CAPTCHA (image-based) and AI-powered Research Paper Recommendation feature (TF-IDF + Cosine Similarity).
