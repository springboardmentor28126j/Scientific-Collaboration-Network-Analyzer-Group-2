# Scientific Research Management System — Backend Plan

## 1. Scope of this phase

Only two things are being built right now:

1. The full **folder structure** of a production-grade FastAPI project.
2. The **auth + institution/user management module** — nothing else (no papers, no reviews, no submissions yet). That comes later once this foundation is solid.

---

## 2. Tech stack

| Concern | Choice |
|---|---|
| Framework | FastAPI |
| Language/runtime | Python 3.12, managed with `uv` |
| DB | PostgreSQL (Render Postgres in prod, local Postgres via Docker in dev) |
| ORM | SQLAlchemy 2.0 (async) + Alembic for migrations |
| Validation | Pydantic v2 (settings via `pydantic-settings`) |
| Auth | JWT (access + refresh) via `python-jose` or `pyjwt`, password hashing via `passlib[bcrypt]` or `argon2-cffi` |
| File storage | Cloudinary (institution logos) |
| Email | `fastapi-mail` (SMTP-based) — MailCatcher in dev, real SMTP (e.g. SES/SendGrid/Mailgun) in prod |
| Background email sending | FastAPI `BackgroundTasks` initially; swappable for Celery/RQ later if needed |
| Containerization | Docker + docker-compose (app, postgres, mailcatcher) |
| Package/dep management | `uv` with `pyproject.toml` + `uv.lock` |
| Testing | `pytest`, `pytest-asyncio`, `httpx.AsyncClient`, `pytest-cov`, test DB via testcontainers or a dedicated docker-compose test service |
| Linting/formatting | `ruff` (lint + format), `mypy` for type checking |
| Deployment target | Render.com (Web Service + Managed Postgres), Dockerfile-based build |
| Docs | Auto OpenAPI/Swagger via FastAPI, plus a `docs/` folder with architecture notes |

---

## 3. Domain model overview

**Actors:**

- **Platform Superuser** — created only from `.env` values at startup (email + password). Has full platform oversight. Not tied to any institution.
- **Institution** — self-registers on the platform (name, logo, address, admin email, admin password). Institution's admin account is created together with the institution record, in a `pending_verification` state.
- **Institution Admin** — the user who registered the institution. Can create Researcher and Reviewer accounts scoped to their own institution, and can activate/deactivate any user (including re-activating itself is not applicable, but can manage others) within that institution.
- **Researcher** — created by an Institution Admin, belongs to that institution, verifies via emailed link, then can log in once activated.
- **Reviewer** — same as Researcher but a different role.

**Key rules:**

- Institution registration triggers an email verification link. Institution admin cannot log in until verified.
- Institution Admin creates Researcher/Reviewer with a basic description at creation time; those users get a verification email link too, and must verify before they can be activated/log in.
- Institution Admin can activate/deactivate accounts under their institution.
- Platform Superuser can activate/deactivate an institution itself (and by extension all its users, or independently — worth deciding: see open question below).
- The **email-verification-on-registration** flow (verifying a brand-new account right after signup) is specific to institutions/institution admins. Researchers/Reviewers instead get an initial "verify to activate" link (invite-style), not a self-registration flow — but once verified, they can log in and use forgot-password like any other verified user.
- Every user record carries a reference to their institution (nullable only for the platform superuser).

**Roles enum:** `SUPER_ADMIN`, `INSTITUTION_ADMIN`, `RESEARCHER`, `REVIEWER`

**User states:** `pending_verification` → `active` (verifying the email link sets both `is_verified=True` and `is_active=True` in one step). Admins/superuser can still manually deactivate an active account later — deactivation is the only separate manual toggle; activation itself happens automatically at verification.

---

## 4. Data model (tables)

**`institutions`**
- id (UUID, PK)
- name
- address
- logo_url (Cloudinary secure URL)
- logo_public_id (Cloudinary asset id, for future deletion/replacement)
- is_active (bool — platform-level kill switch for the whole institution)
- created_at, updated_at

**`users`**
- id (UUID, PK)
- email (unique, used as username)
- hashed_password
- full_name
- role (enum: SUPER_ADMIN / INSTITUTION_ADMIN / RESEARCHER / REVIEWER)
- institution_id (FK → institutions, nullable for SUPER_ADMIN)
- description (nullable — the "basic description" set at creation time for researchers/reviewers)
- is_verified (bool)
- is_active (bool)
- created_at, updated_at

**`email_verification_tokens`**
- id, user_id (FK), token (hashed), purpose (enum: `EMAIL_VERIFY`, `INVITE_VERIFY`), expires_at, used_at

**`password_reset_tokens`**
- id, user_id (FK), token (hashed), expires_at, used_at

Both token tables are kept separate from JWTs — these are single-use, DB-backed, short-lived tokens emailed as links; JWTs are for session auth after login.

---

## 5. Auth & lifecycle flows

**5.1 Platform Superuser bootstrap**
- On app startup (a lifespan hook / startup event), check if a user with `role=SUPER_ADMIN` and the `.env`-defined email exists. If not, create it directly as verified + active, using `SUPERUSER_EMAIL` and `SUPERUSER_PASSWORD` from settings.

**5.2 Institution self-registration**
- `POST /institutions/register` — multipart form: institution name, address, logo file, admin full name, admin email, admin password.
- Logo uploaded to Cloudinary; institution row created (`is_active=True` by default at the institution level, since deactivation is a separate deliberate superuser action); institution admin user row created with `role=INSTITUTION_ADMIN`, `is_verified=False`, `is_active=False`.
- Verification email sent to admin email with a signed/opaque link.

**5.3 Email verification (institution admin)**
- `GET /auth/verify-email?token=...` — validates token, marks `is_verified=True` **and** `is_active=True` in the same step. The institution admin can log in immediately after verifying — no separate manual activation is required for this initial signup flow.

**5.4 Institution Admin creates Researcher/Reviewer**
- `POST /institution/users` (auth: institution admin only) — email, full name, role (RESEARCHER/REVIEWER), description.
- Creates user scoped to `current_user.institution_id`, `is_verified=False`, `is_active=False`, sends an invite-verification email.
- `GET /auth/verify-invite?token=...` — user verifies; account becomes `is_verified=True` **and** `is_active=True` in the same step, so the researcher/reviewer can log in right after verifying. The institution admin's activate/deactivate controls remain available afterward, for cases where the admin wants to suspend access later.

**5.5 Login**
- `POST /auth/login` — OAuth2-password-flow-compatible (email as username). Checks `is_verified` and `is_active`, issues JWT access + refresh tokens.
- `POST /auth/refresh` — exchanges refresh token for new access token.
- Note: this applies equally to institution admins, researchers, and reviewers — role doesn't gate login, only `is_verified` + `is_active` do. A verified researcher or reviewer can also use forgot-password with their own email, same as covered in §5.6 below.

**5.6 Forgot password (any verified user — institution admin, researcher, or reviewer)**
- `POST /auth/forgot-password` — email input, sends reset link if a **verified** account exists for that email, regardless of role (generic response either way, to avoid user enumeration).
- `POST /auth/reset-password` — token + new password.
- Note: researchers/reviewers only reach this point once they've verified via their invite link — an unverified account has no password to reset yet, so this naturally excludes `pending_verification` users without needing a separate rule.

**5.7 Activate / deactivate**

Split strictly by scope — the superuser never manages researchers/reviewers directly; that's always the institution admin's responsibility within their own institution.

- `PATCH /institution/users/{user_id}/activate` and `.../deactivate` — institution admin, scoped to own institution (this is the *only* path for suspending/reinstating a researcher or reviewer).
- `PATCH /admin/institutions/{institution_id}/activate` / `.../deactivate` — superuser only, toggles the institution (and practically locks out all its users at auth-check time).
- `PATCH /admin/institution-admins/{user_id}/activate` / `.../deactivate` — superuser toggling an institution admin specifically.

**Resolved:** verifying an email auto-activates the account (both `is_verified` and `is_active` flip to `True` together). Activate/deactivate controls after this point are split by scope: the **superuser** only ever touches institutions and institution admins (§5.7) — it has no direct authority over researchers or reviewers. Managing researcher/reviewer accounts (suspending, reactivating) is entirely the **institution admin's** job, scoped to their own institution. This keeps the superuser's blast radius limited to institution-level oversight rather than reaching into every institution's internal user management.

---

## 6. Folder structure

```
research-mgmt-system/
├── app/
│   ├── main.py                     # FastAPI app factory, router registration, startup events
│   ├── core/
│   │   ├── config.py                # pydantic-settings, reads .env
│   │   ├── security.py              # password hashing, JWT create/verify
│   │   ├── dependencies.py          # get_current_user, role-based guards, per-request institution is_active check
│   │   └── exceptions.py            # custom exception classes + handlers
│   ├── db/
│   │   ├── base.py                  # SQLAlchemy declarative base, import registry
│   │   ├── session.py               # async engine + session factory
│   │   └── init_db.py               # superuser bootstrap logic
│   ├── models/
│   │   ├── institution.py
│   │   ├── user.py
│   │   └── token.py                 # verification + reset tokens
│   ├── schemas/
│   │   ├── institution.py
│   │   ├── user.py
│   │   ├── auth.py
│   │   └── common.py                # shared response envelopes, pagination
│   ├── repositories/
│   │   ├── institution_repository.py
│   │   ├── user_repository.py
│   │   └── token_repository.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── institution_service.py
│   │   ├── user_service.py
│   │   ├── email_service.py
│   │   └── cloudinary_service.py
│   ├── api/
│   │   ├── deps.py                  # shared FastAPI Depends wiring
│   │   └── v1/
│   │       ├── router.py            # aggregates all v1 routers
│   │       ├── auth.py              # login, refresh, verify, forgot/reset password
│   │       ├── institutions.py      # self-registration
│   │       └── institution_users.py # institution admin managing researchers/reviewers
│   ├── templates/
│   │   └── emails/
│   │       ├── verify_email.html
│   │       ├── verify_invite.html
│   │       └── reset_password.html
│   └── middleware/
│       └── logging_middleware.py
├── alembic/
│   ├── versions/
│   └── env.py
├── tests/
│   ├── conftest.py                  # test client, test DB fixtures
│   ├── test_auth.py
│   ├── test_institutions.py
│   └── test_institution_users.py
├── scripts/
│   └── wait_for_db.sh
├── docs/
│   └── architecture.md
├── .env.example
├── alembic.ini
├── docker-compose.yml
├── docker-compose.test.yml
├── Dockerfile
├── pyproject.toml
├── uv.lock
└── README.md
```

**Why this shape:**
- `models` (DB layer) is kept separate from `schemas` (API contracts) — standard FastAPI production pattern, avoids leaking DB internals through the API.
- `repositories` isolate raw DB queries; `services` hold business logic (e.g., "registering an institution" touches Cloudinary + DB + email — that orchestration lives in the service, not the route).
- `api/v1` versioning from day one, since research platforms tend to evolve their contracts.
- `templates/emails` as HTML files rather than inline strings, rendered with Jinja2 through `fastapi-mail`.

---

## 7. Environment variables (`.env.example`)

```
ENVIRONMENT=development
DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/research_db
SECRET_KEY=
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

SUPERUSER_EMAIL=admin@platform.com
SUPERUSER_PASSWORD=changeme

CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_FROM=noreply@platform.com
MAIL_SERVER=mailcatcher     # smtp.<provider>.com in prod
MAIL_PORT=1025               # 587 in prod
MAIL_STARTTLS=False
MAIL_SSL_TLS=False

FRONTEND_URL=http://localhost:3000   # used to build verification/reset links
```

---

## 8. Docker setup

**Services in `docker-compose.yml` (dev):**
- `app` — built from `Dockerfile`, mounts source for hot reload, depends on `db` and `mailcatcher`.
- `db` — `postgres:16-alpine`, named volume for persistence.
- `mailcatcher` — SMTP on 1025, web UI on 1080, so all verification/reset emails during dev are viewable in-browser instead of hitting real inboxes.

**`Dockerfile`:** multi-stage, using `uv` to install dependencies into a slim runtime image (builder stage installs deps with `uv sync --frozen`, final stage copies the venv + app code, runs via `uvicorn` with a non-root user).

**`docker-compose.test.yml`:** spins up an isolated Postgres on a different port for the test suite, so tests never touch dev data.

**Render.com deployment:**
- Render Web Service builds directly from the `Dockerfile`.
- Render Managed Postgres provides `DATABASE_URL` as an env var.
- Alembic migrations run as a Render "Pre-Deploy Command" (or a release-phase script) before the new instance takes traffic.
- Real SMTP provider env vars replace the MailCatcher ones in Render's dashboard.

---

## 9. Testing strategy

- `pytest-asyncio` + `httpx.AsyncClient` against the FastAPI app with `ASGITransport`, no real network calls.
- A fixture spins up a fresh test DB schema per test session (or per test with transactional rollback) — via the `docker-compose.test.yml` Postgres.
- Cloudinary and email calls are mocked in unit/integration tests (dependency-injected services make this easy to patch).
- Coverage target and `pytest-cov` wired into CI later.
- Test files mirror the `api/v1` structure: registration, verification, login, forgot/reset password, activate/deactivate, role-guard enforcement (e.g., a researcher hitting an institution-admin-only route gets 403).

---

## 10. Documentation

- FastAPI's built-in OpenAPI docs (`/docs`, `/redoc`) — every route gets a summary, description, and response model so this is genuinely useful, not just default-generated.
- `docs/architecture.md` — the content of this plan, kept in-repo and updated as the system grows.
- `README.md` — local dev setup (`uv sync`, `docker compose up`), running migrations, running tests, MailCatcher usage instructions.

---

## 11. Build order (once you confirm this plan)

1. Scaffold the folder structure + `pyproject.toml` + Docker/compose files, get `docker compose up` running an empty FastAPI app talking to Postgres and MailCatcher.
2. Models + Alembic migration for `institutions`, `users`, `email_verification_tokens`, `password_reset_tokens`.
3. Core: config, security (hashing + JWT), superuser bootstrap on startup.
4. Institution self-registration endpoint (Cloudinary upload + email verification send).
5. Email verification + login + refresh.
6. Forgot/reset password for institution admins.
7. Institution admin creating researchers/reviewers + invite verification.
8. Activate/deactivate endpoints (institution-scoped and platform-scoped).
9. Tests for every flow above.
10. README + architecture docs pass.

---

## 12. Things worth deciding before coding starts

1. **Resolved:** a deactivated institution instantly rejects its users' JWTs — not just new logins. This means the auth dependency (`app/core/dependencies.py`) must check the institution's `is_active` flag (in addition to the user's own `is_active`/`is_verified`) on every authenticated request, not only at login time. Existing access tokens for that institution's users become worthless the moment the institution is deactivated, even if the token itself hasn't expired yet.
2. Password policy (min length/complexity) — enforce in the Pydantic schema with a validator.
3. JWT storage strategy on the client side — not a backend concern, but affects whether refresh tokens are rotated/blacklisted on logout (worth a `token_blacklist` table if you want real logout, otherwise access tokens just expire naturally).

Once you confirm the open questions in §5 and §12, I'll start implementing in the build order above.
