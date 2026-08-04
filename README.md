# Scientific Collaboration Network Analyzer

A FastAPI web application for managing researchers, institutions, publications, conferences, research projects, citations, and collaboration networks.

## Demo-ready modules (Milestones 1–3)

- User registration and password-hashed login with JWT access tokens
- Researcher profiles and institution affiliation management
- Institution CRUD and institution-level reports
- Publication CRUD, DOI duplicate protection, author assignment/removal, status filters, and PDF uploads
- Conference creation and researcher participation records
- Co-author collaboration network with interactive graph data
- Project creation and researcher project assignments
- Citation records, dashboard statistics, activity notifications, and report counters

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and set `DATABASE_URL`. If it is omitted, the app uses a local SQLite file.
4. Start the API:

   ```powershell
   uvicorn app.main:app --reload
   ```

5. Open API documentation at `http://127.0.0.1:8000/docs` or the web UI at `http://127.0.0.1:8000/frontend/index.html`.

## Important routes

- `/dashboard/` – dashboard counts
- `/researchers/`, `/institutions/`, `/publications/`, `/conferences/`
- `/collaborations/network/advanced` – visualization data
- `/projects/` and `/projects/{project_id}/assignments`
- `/citations/`, `/reports/`, `/notifications/`
