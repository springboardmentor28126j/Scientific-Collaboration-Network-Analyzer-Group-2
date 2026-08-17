"""
Flask frontend for the Scientific Collaboration Network Analyzer (Milestone 1).

Wired to the FastAPI backend: login/register/profile now call the real API
and store the JWT access token in the Flask session.
"""
import os

import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash, Response, jsonify, g, abort

from flask_wtf import CSRFProtect

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
from datetime import timedelta
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=14)
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("FLASK_ENV") == "production"

csrf = CSRFProtect(app)

BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
RECAPTCHA_SITE_KEY = os.environ.get("RECAPTCHA_SITE_KEY", "")
RECAPTCHA_SECRET_KEY = os.environ.get("RECAPTCHA_SECRET_KEY", "")


def _verify_recaptcha(token: str) -> bool:
    if not RECAPTCHA_SECRET_KEY:
        return True  # captcha not configured — don't lock out local dev
    if not token:
        return False
    try:
        resp = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={"secret": RECAPTCHA_SECRET_KEY, "response": token},
            timeout=10,
        )
        return resp.json().get("success", False)
    except requests.RequestException:
        return False


def _honeypot_tripped() -> bool:
    return bool(request.form.get("website", "").strip())


def _auth_headers() -> dict:
    token = session.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}


@app.route("/uploads/<path:filepath>")
def serve_upload(filepath):
    """Proxies uploaded files (publication PDFs, presentation slides, etc.)
    through the frontend instead of linking straight to BACKEND_URL.

    Templates used to build links as ``{{ backend_url }}{{ item.file_url }}``.
    BACKEND_URL is set for server-to-server calls (e.g. the docker-compose
    value ``http://backend:8000``, which only resolves *inside* the docker
    network) and is not necessarily reachable from the user's browser, so
    clicking those links could fail even though the upload itself worked.
    Routing the download through this frontend endpoint means the browser
    only ever talks to the frontend's own host, and this view does the
    backend fetch server-side where BACKEND_URL is guaranteed to resolve.
    """
    if not session.get("token"):
        return redirect(url_for("login"))
    try:
        resp = requests.get(f"{BACKEND_URL}/uploads/{filepath}", timeout=15)
    except requests.RequestException:
        abort(502)
    if resp.status_code != 200:
        abort(404)
    return Response(
        resp.content,
        mimetype=resp.headers.get("Content-Type", "application/octet-stream"),
        headers={"Content-Disposition": resp.headers.get("Content-Disposition", "inline")},
    )

def _current_role():
    """The logged-in user's role ('researcher', 'institution_admin',
    'reviewer', 'system_admin'), or None if not logged in. Cached per
    request so templates and routes can both call this cheaply."""
    if not session.get("token"):
        return None
    if not hasattr(g, "_researcher_cache"):
        g._researcher_cache = _current_researcher()
    researcher = g._researcher_cache
    return researcher.get("user", {}).get("role") if researcher else None


def _current_user_id():
    """The logged-in user's numeric id, or None if not logged in."""
    if not session.get("token"):
        return None
    if not hasattr(g, "_researcher_cache"):
        g._researcher_cache = _current_researcher()
    researcher = g._researcher_cache
    return researcher.get("user_id") if researcher else None


def _unread_notification_count():
    if not session.get("token"):
        return 0
    resp = requests.get(
        f"{BACKEND_URL}/notifications/unread-count", headers=_auth_headers(), timeout=5
    )
    return resp.json().get("unread_count", 0) if resp.status_code == 200 else 0


@app.context_processor
def inject_role():
    return {
        "current_role": _current_role(),
        "current_user_id": _current_user_id(),
        "unread_notification_count": _unread_notification_count(),
        "backend_url": BACKEND_URL,
    }

# -----------------------------
# Sorting / Pagination helpers
# -----------------------------
MAX_PER_PAGE = 10
DEFAULT_PER_PAGE = 5
STATUS_PILL_CLASS = {
    "registered": "pill-teal",
    "confirmed": "pill-teal",
    "attended": "pill-blue",
    "cancelled": "pill-gray",
}

ROLE_PILL_CLASS = {
    "researcher": "pill-gray",
    "institution_admin": "pill-purple",
    "reviewer": "pill-blue",
    "system_admin": "pill-teal",
}

ROLE_LABEL = {
    "researcher": "Researcher",
    "institution_admin": "Institution Admin",
    "reviewer": "Reviewer",
    "system_admin": "System Admin",
}


def _sort_key(value):
    """Push None values to the end regardless of field type."""
    if value is None:
        return (1, "")
    if isinstance(value, (int, float)):
        return (0, value)
    return (0, str(value).lower())


def _sort_items(items, sort_by, sort_order, allowed_fields, default_field):
    field = sort_by if sort_by in allowed_fields else default_field
    reverse = sort_order == "desc"
    return sorted(items, key=lambda item: _sort_key(item.get(field)), reverse=reverse)


def _page_window(current, total_pages, spread=2):
    """[1, None, 4, 5, 6, 7, 8, None, 20] -- None means an ellipsis."""
    pages = []
    for p in range(1, total_pages + 1):
        if p == 1 or p == total_pages or (current - spread <= p <= current + spread):
            pages.append(p)
        elif pages and pages[-1] is not None:
            pages.append(None)
    return pages


def _paginate(items, request):
    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1
    try:
        per_page = int(request.args.get("per_page", DEFAULT_PER_PAGE))
    except ValueError:
        per_page = DEFAULT_PER_PAGE

    per_page = max(1, min(per_page, MAX_PER_PAGE))
    page = max(1, page)

    total = len(items)
    total_pages = max(1, -(-total // per_page))
    page = min(page, total_pages)

    start = (page - 1) * per_page
    end = start + per_page

    pagination = {
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
        "has_prev": page > 1,
        "has_next": page < total_pages,
        "start_index": (start + 1) if total else 0,
        "end_index": min(end, total),
        "page_numbers": _page_window(page, total_pages),
    }
    return items[start:end], pagination


def _pagination_args(request):
    args = request.args.to_dict()
    args.pop("page", None)
    return args

@app.route("/")
def index():
    if session.get("token"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        show_captcha = session.get("show_captcha", False)

        if show_captcha:
            if _honeypot_tripped():
                flash("Something went wrong. Please try again.", "error")
                return redirect(url_for("login"))
            if not _verify_recaptcha(request.form.get("g-recaptcha-response", "")):
                flash("Please complete the CAPTCHA verification.", "error")
                return redirect(url_for("login"))

        email = request.form.get("email", "")
        password = request.form.get("password", "")
        try:
            resp = requests.post(
                f"{BACKEND_URL}/auth/login",
                data={"username": email, "password": password},
                timeout=10,
            )
        except requests.RequestException:
            flash("Could not reach the backend. Is it running on BACKEND_URL?", "error")
            return redirect(url_for("login"))

        if resp.status_code != 200:
            fail_count = session.get("login_fail_count", 0) + 1
            session["login_fail_count"] = fail_count
            if fail_count >= 2:
                session["show_captcha"] = True

            detail = resp.json().get("detail", "Incorrect email or password.") if resp.content else "Incorrect email or password."
            flash(detail, "error")
            if resp.status_code == 403 and "verify" in detail.lower():
                session["unverified_email"] = email
            return redirect(url_for("login"))

        session.pop("login_fail_count", None)
        session.pop("show_captcha", None)

        data = resp.json()
        if data.get("mfa_required"):
            session["pre_auth_token"] = data["pre_auth_token"]
            session["pre_auth_email"] = email
            return redirect(url_for("mfa_verify"))
        session["token"] = data["access_token"]
        session["email"] = email
        session.permanent = bool(request.form.get("remember_me"))

        me_resp = requests.get(f"{BACKEND_URL}/auth/me", headers=_auth_headers(), timeout=10)
        role = me_resp.json().get("role") if me_resp.status_code == 200 else None
        if role in ("system_admin", "institution_admin"):
            flash("Two-factor authentication is required for admin accounts. We'll set it up now — check your email for a confirmation code after you continue.", "error")
            enable_resp = requests.post(f"{BACKEND_URL}/auth/mfa/enable", headers=_auth_headers(), timeout=10)

        flash("Logged in successfully.", "success")
        return redirect(url_for("dashboard"))

    return render_template(
        "login.html",
        unverified_email=session.pop("unverified_email", None),
        google_client_id=GOOGLE_CLIENT_ID,
        recaptcha_site_key=RECAPTCHA_SITE_KEY,
        show_captcha=session.get("show_captcha", False),
    )


@app.route("/mfa/verify", methods=["GET", "POST"])
def mfa_verify():
    pre_auth_token = session.get("pre_auth_token")
    if not pre_auth_token:
        return redirect(url_for("login"))

    if request.method == "POST":
        code = request.form.get("code", "")
        resp = requests.post(
            f"{BACKEND_URL}/auth/mfa/verify-login",
            json={"pre_auth_token": pre_auth_token, "code": code},
            timeout=10,
        )
        if resp.status_code != 200:
            flash("Invalid or expired code. Please try again.", "error")
            return redirect(url_for("mfa_verify"))

        data = resp.json()
        session["token"] = data["access_token"]
        session["email"] = session.pop("pre_auth_email", "")
        session.pop("pre_auth_token", None)
        flash("Logged in successfully.", "success")
        return redirect(url_for("dashboard"))

    return render_template("mfa_verify.html", pre_auth_token=pre_auth_token)


@app.route("/mfa/resend", methods=["POST"])
def mfa_resend():
    pre_auth_token = request.form.get("pre_auth_token") or session.get("pre_auth_token")
    if not pre_auth_token:
        return redirect(url_for("login"))
    requests.post(f"{BACKEND_URL}/auth/mfa/resend-otp", json={"pre_auth_token": pre_auth_token}, timeout=10)
    flash("A new code has been sent to your email.", "success")
    session["pre_auth_token"] = pre_auth_token
    return redirect(url_for("mfa_verify"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if _honeypot_tripped():
            flash("Something went wrong. Please try again.", "error")
            return redirect(url_for("register"))
        if not _verify_recaptcha(request.form.get("g-recaptcha-response", "")):
            flash("Please complete the CAPTCHA verification.", "error")
            return redirect(url_for("register"))
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        role = request.form.get("role", "researcher")
        institution_id = _to_int_or_none(request.form.get("institution_id"))

        payload = {"email": email, "password": password, "role": role}
        if role == "institution_admin":
            payload["institution_id"] = institution_id

        try:
            resp = requests.post(f"{BACKEND_URL}/auth/register", json=payload, timeout=10)
        except requests.RequestException:
            flash("Could not reach the backend. Is it running on BACKEND_URL?", "error")
            return redirect(url_for("register"))

        if resp.status_code != 201:
            detail = resp.json().get("detail", "Registration failed.") if resp.content else "Registration failed."
            flash(detail, "error")
            return redirect(url_for("register"))

        data = resp.json()
        if data.get("is_active") is False:
            flash("Application submitted — awaiting System Admin approval before you can log in.", "success")
        else:
            flash("Account created! Check your email to verify your account before logging in.", "success")
        return redirect(url_for("login"))

    inst_resp = requests.get(f"{BACKEND_URL}/institutions/public", timeout=10)
    institutions = inst_resp.json() if inst_resp.status_code == 200 else []
    return render_template("register.html", institutions=institutions, google_client_id=GOOGLE_CLIENT_ID, recaptcha_site_key=RECAPTCHA_SITE_KEY)


@app.route("/dashboard")
def dashboard():
    if not session.get("token"):
        return redirect(url_for("login"))

    resp = requests.get(f"{BACKEND_URL}/researchers/me", headers=_auth_headers(), timeout=10)
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))

    researcher = resp.json() if resp.status_code == 200 else {}
    user = researcher.get("user", {"email": session.get("email"), "role": "researcher"})
    role = user.get("role", "researcher")

    admin_stats = None
    reviewer_pending_count = None
    reviewer_reviewed_count = None
    project_count = None
    collaborator_count = None
    publication_count = None
    institution = None
    institution_reviewer_count = None

    if role == "system_admin":
        _, admin_stats = _admin_user_stats()

    elif role == "reviewer":
        rq = requests.get(
            f"{BACKEND_URL}/publications/pending-review", headers=_auth_headers(), timeout=10
        )
        reviewer_pending_count = len(rq.json()) if rq.status_code == 200 else 0

        rvd = requests.get(
            f"{BACKEND_URL}/publications/reviewed-by-me", headers=_auth_headers(), timeout=10
        )
        reviewer_reviewed_count = len(rvd.json()) if rvd.status_code == 200 else 0

    elif role == "institution_admin":
        inst_resp = requests.get(f"{BACKEND_URL}/institutions/mine", headers=_auth_headers(), timeout=10)
        institutions = inst_resp.json() if inst_resp.status_code == 200 else []
        institution = institutions[0] if institutions else None

        if institution:
            ra_resp = requests.get(
                f"{BACKEND_URL}/reviewer-assignments",
                params={"institution_id": institution["id"]},
                headers=_auth_headers(),
                timeout=10,
            )
            institution_reviewer_count = len(ra_resp.json()) if ra_resp.status_code == 200 else 0

    else:  # researcher
        pub_resp = requests.get(
            f"{BACKEND_URL}/publications", params={"author_id": researcher.get("id")}, headers=_auth_headers(), timeout=10
        )
        publication_count = len(pub_resp.json()) if pub_resp.status_code == 200 else 0

        proj_resp = requests.get(f"{BACKEND_URL}/projects", headers=_auth_headers(), timeout=10)
        project_count = len(proj_resp.json()) if proj_resp.status_code == 200 else 0

        collab_resp = requests.get(
            f"{BACKEND_URL}/collaborations/my", params={"page": 1, "page_size": 10}, headers=_auth_headers(), timeout=10
        )
        collaborator_count = collab_resp.json().get("total", 0) if collab_resp.status_code == 200 else 0

    return render_template(
        "dashboard.html",
        user=user,
        admin_stats=admin_stats,
        reviewer_pending_count=reviewer_pending_count,
        reviewer_reviewed_count=reviewer_reviewed_count,
        project_count=project_count,
        collaborator_count=collaborator_count,
        publication_count=publication_count,
        institution=institution,
        institution_reviewer_count=institution_reviewer_count,
    )

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if not session.get("token"):
        return redirect(url_for("login"))

    role = _current_role()

    if role == "institution_admin":
        inst_resp = requests.get(f"{BACKEND_URL}/institutions/mine", headers=_auth_headers(), timeout=10)
        institutions = inst_resp.json() if inst_resp.status_code == 200 else []
        if institutions:
            return redirect(url_for("edit_institution", institution_id=institutions[0]["id"]))
        flash("No institution is linked to your account yet. Contact a System Admin.", "error")
        return redirect(url_for("dashboard"))

    if role == "reviewer":
        user_id = _current_user_id()

        me_resp = requests.get(f"{BACKEND_URL}/researchers/me", headers=_auth_headers(), timeout=10)
        me = me_resp.json().get("user", {}) if me_resp.status_code == 200 else {}

        ra_resp = requests.get(
            f"{BACKEND_URL}/reviewer-assignments", params={"reviewer_user_id": user_id}, headers=_auth_headers(), timeout=10
        )
        assignments = ra_resp.json() if ra_resp.status_code == 200 else []

        inst_resp = requests.get(f"{BACKEND_URL}/institutions/", headers=_auth_headers(), timeout=10)
        institutions = inst_resp.json() if inst_resp.status_code == 200 else []
        institution_lookup = {i["id"]: i["name"] for i in institutions}

        pub_resp = requests.get(f"{BACKEND_URL}/publications/pending-review", headers=_auth_headers(), timeout=10)
        pending = pub_resp.json() if pub_resp.status_code == 200 else []

        types_seen = sorted({p["type"] for p in pending if p.get("type")})
        venues_seen = sorted({p["venue"] for p in pending if p.get("venue")})

        for a in assignments:
            a["institution_name"] = institution_lookup.get(a["institution_id"]) if a.get("institution_id") else None

        return render_template(
            "profile_reviewer.html",
            user_id=user_id,
            email=me.get("email"),
            assignments=assignments,
            pending_count=len(pending),
            types_seen=types_seen,
            venues_seen=venues_seen,
        )

    if request.method == "POST":
        payload = {
            "department": request.form.get("department") or None,
            "institution_id": _to_int_or_none(request.form.get("institution_id")),
            "research_interests": request.form.get("research_interests") or None,
            "skills": request.form.get("skills") or None,
            "affiliations": request.form.get("affiliations") or None,
        }
        resp = requests.put(
            f"{BACKEND_URL}/researchers/me",
            json=payload,
            headers=_auth_headers(),
            timeout=10,
        )
        if resp.status_code == 401:
            session.clear()
            flash("Session expired. Please log in again.", "error")
            return redirect(url_for("login"))
        if resp.status_code != 200:
            flash("Could not save profile.", "error")
        else:
            flash("Profile saved.", "success")
        return redirect(url_for("profile"))

    resp = requests.get(f"{BACKEND_URL}/researchers/me", headers=_auth_headers(), timeout=10)
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))

    researcher = resp.json() if resp.status_code == 200 else {}
    return render_template("profile.html", researcher=researcher)


def _to_int_or_none(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except ValueError:
        return None


@app.route("/security", methods=["GET", "POST"])
def security_settings():
    if not session.get("token"):
        return redirect(url_for("login"))

    me_resp = requests.get(f"{BACKEND_URL}/auth/me", headers=_auth_headers(), timeout=10)
    if me_resp.status_code != 200:
        flash("Could not load your account details.", "error")
        return redirect(url_for("dashboard"))
    me = me_resp.json()
    is_admin_role = me.get("role") in ("system_admin", "institution_admin")

    if request.method == "POST":
        action = request.form.get("action")
        if action == "disable" and is_admin_role:
            flash("Two-factor authentication is required for admin accounts.", "error")
            return redirect(url_for("security_settings"))

        endpoint = "enable" if action == "enable" else "disable"
        requests.post(f"{BACKEND_URL}/auth/mfa/{endpoint}", headers=_auth_headers(), timeout=10)
        flash(f"Two-factor authentication {'enabled' if endpoint == 'enable' else 'disabled'}.", "success")
        return redirect(url_for("security_settings"))

    return render_template("security_settings.html", mfa_enabled=me.get("mfa_enabled", False), is_admin_role=is_admin_role)
    

@app.route("/institution", methods=["GET", "POST"])
def institution():

    if not session.get("token"):
        return redirect(url_for("login"))

    # -----------------------------
    # Create Institution
    # -----------------------------
    if request.method == "POST":

        payload = {
            "name": request.form.get("name"),
            "short_name": request.form.get("short_name") or None,
            "institution_type": request.form.get("institution_type") or None,
            "email": request.form.get("email"),
            "phone": request.form.get("phone") or None,
            "website": request.form.get("website") or None,
            "address": request.form.get("address") or None,
            "city": request.form.get("city"),
            "state": request.form.get("state"),
            "country": request.form.get("country"),
            "postal_code": request.form.get("postal_code") or None,
            "status": "Active",
        }

        try:

            response = requests.post(
                f"{BACKEND_URL}/institutions/",
                json=payload,
                headers=_auth_headers(),
                timeout=10,
            )

            if response.status_code == 201:
                flash("Institution created successfully.", "success")

            elif response.status_code == 400:
                detail = response.json().get("detail", "Institution already exists.")
                flash(detail, "error")

            elif response.status_code == 401:
                session.clear()
                flash("Session expired. Please login again.", "error")
                return redirect(url_for("login"))

            else:
                flash("Unable to create institution.", "error")

        except requests.RequestException:
            flash("Backend server is not running.", "error")

        return redirect(url_for("institution"))

    # -----------------------------
    # Search / List Institutions
    # -----------------------------
    search = request.args.get("search", "").strip()

    try:

        if search:

            response = requests.get(
                f"{BACKEND_URL}/institutions/search/",
                params={"name": search},
                headers=_auth_headers(),
                timeout=10,
            )
            print("Search:", search)
            print("Status Code:", response.status_code)
            print("Response JSON:", response.text)

        else:

            response = requests.get(
                f"{BACKEND_URL}/institutions/",
                headers=_auth_headers(),
                timeout=10,
            )

        if response.status_code == 401:
            session.clear()
            flash("Session expired. Please login again.", "error")
            return redirect(url_for("login"))

        if response.status_code == 200:
            institutions = response.json()
        else:
            institutions = []

    except requests.RequestException:
        institutions = []
        flash("Backend server is not running.", "error")

    # -----------------------------
    # Get Logged-in User Role
    # -----------------------------
    user = {}
    try:
        resp = requests.get(
            f"{BACKEND_URL}/researchers/me",
            headers=_auth_headers(),
            timeout=10,
        )
        if resp.status_code == 200:
            researcher = resp.json()
            user = researcher.get("user", {})
    except requests.RequestException:
        pass

    return render_template(
        "institution.html",
        institutions=institutions,
        search=search,
        user=user,
    )

    return render_template(
        "institution.html",
        institutions=institutions,
        search=search,
    )

@app.route("/institution/edit/<int:institution_id>")
def edit_institution(institution_id):

    if not session.get("token"):
        return redirect(url_for("login"))

    try:

        response = requests.get(
            f"{BACKEND_URL}/institutions/{institution_id}",
            headers=_auth_headers(),
            timeout=10,
        )

        if response.status_code == 401:
            session.clear()
            flash("Session expired. Please login again.", "error")
            return redirect(url_for("login"))

        if response.status_code != 200:
            flash("Institution not found.", "error")
            return redirect(url_for("institution"))

        institution = response.json()

    except requests.RequestException:
        flash("Backend server is not running.", "error")
        return redirect(url_for("institution"))

    institution_admins = []
    if _current_role() == "system_admin":
        users_resp = requests.get(
            f"{BACKEND_URL}/admin/users", headers=_auth_headers(), timeout=10
        )
        if users_resp.status_code == 200:
            institution_admins = [
                u for u in users_resp.json() if u.get("role") == "institution_admin"
            ]

    return render_template(
        "edit_institution.html",
        institution=institution,
        institution_admins=institution_admins,
    )

@app.route("/institution/update/<int:institution_id>", methods=["POST"])
def update_institution(institution_id):

    if not session.get("token"):
        return redirect(url_for("login"))

    payload = {
        "name": request.form.get("name"),
        "short_name": request.form.get("short_name") or None,
        "institution_type": request.form.get("institution_type") or None,
        "email": request.form.get("email"),
        "phone": request.form.get("phone") or None,
        "website": request.form.get("website") or None,
        "address": request.form.get("address") or None,
        "city": request.form.get("city"),
        "state": request.form.get("state"),
        "country": request.form.get("country"),
        "postal_code": request.form.get("postal_code") or None,
        "status": request.form.get("status") or "Active",
    }

    if "admin_user_id" in request.form:
        payload["admin_user_id"] = _to_int_or_none(request.form.get("admin_user_id"))

    try:

        response = requests.put(
            f"{BACKEND_URL}/institutions/{institution_id}",
            json=payload,
            headers=_auth_headers(),
            timeout=10,
        )

        if response.status_code == 200:
            flash("Institution updated successfully.", "success")

        elif response.status_code == 400:
            detail = response.json().get("detail", "Unable to update institution.")
            flash(detail, "error")

        elif response.status_code == 404:
            flash("Institution not found.", "error")

        elif response.status_code == 401:
            session.clear()
            flash("Session expired. Please login again.", "error")
            return redirect(url_for("login"))

        else:
            flash("Unable to update institution.", "error")

    except requests.RequestException:
        flash("Backend server is not running.", "error")

    return redirect(url_for("institution"))

@app.route("/institution/delete/<int:institution_id>", methods=["POST"])
def delete_institution(institution_id):

    if not session.get("token"):
        return redirect(url_for("login"))

    try:

        response = requests.delete(
            f"{BACKEND_URL}/institutions/{institution_id}",
            headers=_auth_headers(),
            timeout=10,
        )

        if response.status_code == 200:
            flash(
                "Institution deleted successfully.",
                "success",
            )

        elif response.status_code == 404:
            flash(
                "Institution not found.",
                "error",
            )

        elif response.status_code == 401:

            session.clear()

            flash(
                "Session expired. Please login again.",
                "error",
            )

            return redirect(url_for("login"))

        else:

            flash(
                "Unable to delete institution.",
                "error",
            )

    except requests.RequestException:

        flash(
            "Backend server is not running.",
            "error",
        )

    return redirect(url_for("institution"))


@app.route("/institutions/collaborations", methods=["GET", "POST"])
def institution_collaborations():
    if not session.get("token"):
        return redirect(url_for("login"))

    if request.method == "POST":
        my_institution_id = request.form.get("my_institution_id")
        payload = {
            "partner_institution_id": int(request.form.get("partner_institution_id")),
            "title": request.form.get("title"),
            "description": request.form.get("description") or None,
            "start_date": request.form.get("start_date") or None,
            "end_date": request.form.get("end_date") or None,
        }
        try:
            resp = requests.post(
                f"{BACKEND_URL}/institution-collaborations",
                params={"my_institution_id": my_institution_id},
                json=payload,
                headers=_auth_headers(),
                timeout=10,
            )
            if resp.status_code == 201:
                flash("Partnership proposal sent.", "success")
            elif resp.status_code == 401:
                session.clear()
                flash("Session expired. Please log in again.", "error")
                return redirect(url_for("login"))
            else:
                flash(resp.json().get("detail", "Could not create the partnership."), "error")
        except requests.RequestException:
            flash("Backend server is not running.", "error")
        return redirect(url_for("institution_collaborations"))

    try:
        institutions_resp = requests.get(f"{BACKEND_URL}/institutions/", headers=_auth_headers(), timeout=10)
        all_institutions = institutions_resp.json() if institutions_resp.status_code == 200 else []
    except requests.RequestException:
        all_institutions = []
        flash("Backend server is not running.", "error")

    me_resp = requests.get(f"{BACKEND_URL}/auth/me", headers=_auth_headers(), timeout=10)
    me = me_resp.json() if me_resp.status_code == 200 else {}
    current_user_id = me.get("id")
    is_system_admin = me.get("role") == "system_admin"

    my_institutions = all_institutions if is_system_admin else [
        i for i in all_institutions if i.get("admin_user_id") == current_user_id
    ]

    filter_institution_id = request.args.get("institution_id", type=int)
    try:
        params = {"institution_id": filter_institution_id} if filter_institution_id else {}
        collab_resp = requests.get(f"{BACKEND_URL}/institution-collaborations", params=params, headers=_auth_headers(), timeout=10)
        collaborations = collab_resp.json() if collab_resp.status_code == 200 else []
    except requests.RequestException:
        collaborations = []

    return render_template(
        "institution_collaborations.html",
        collaborations=collaborations,
        my_institutions=my_institutions,
        all_institutions=all_institutions,
        filter_institution_id=filter_institution_id,
        current_user_id=current_user_id,
    )


@app.route("/institutions/collaborations/<int:collaboration_id>/status", methods=["POST"])
def update_institution_collaboration_status(collaboration_id):
    if not session.get("token"):
        return redirect(url_for("login"))

    new_status = request.form.get("status")
    try:
        resp = requests.patch(
            f"{BACKEND_URL}/institution-collaborations/{collaboration_id}/status",
            json={"status": new_status},
            headers=_auth_headers(),
            timeout=10,
        )
        if resp.status_code == 200:
            flash(f"Partnership marked as {new_status}.", "success")
        elif resp.status_code == 401:
            session.clear()
            flash("Session expired. Please log in again.", "error")
            return redirect(url_for("login"))
        else:
            flash(resp.json().get("detail", "Could not update status."), "error")
    except requests.RequestException:
        flash("Backend server is not running.", "error")

    return redirect(url_for("institution_collaborations"))


def _parse_coauthor_ids(raw: str) -> list[int]:
    return [int(part.strip()) for part in raw.split(",") if part.strip().isdigit()]


def _current_researcher():
    """Fetch the logged-in user's researcher profile, or None if not created yet."""
    resp = requests.get(f"{BACKEND_URL}/researchers/me", headers=_auth_headers(), timeout=10)
    if resp.status_code == 200:
        return resp.json()
    return None


@app.route("/publications")
def publications():
    if not session.get("token"):
        return redirect(url_for("login"))

    researcher = _current_researcher()
    researcher_id = researcher.get("id") if researcher else None

    params = {}
    if researcher_id:
        params["author_id"] = researcher_id
    if request.args.get("q"):
        params["q"] = request.args["q"]
    if request.args.get("year"):
        params["year"] = request.args["year"]

    pubs = []
    if researcher_id:
        resp = requests.get(f"{BACKEND_URL}/publications", params=params, timeout=10)
        if resp.status_code == 200:
            pubs = resp.json()
    else:
        flash("Create your researcher profile before adding publications.", "error")

    sort_by = request.args.get("sort_by", "year")
    sort_order = request.args.get("sort_order", "desc")
    allowed_sort_fields = {"title", "year", "venue", "status"}
    if sort_by not in allowed_sort_fields:
        sort_by = "year"
    if sort_order not in {"asc", "desc"}:
        sort_order = "desc"

    pubs = _sort_items(pubs, sort_by, sort_order, allowed_sort_fields, "year")
    total_count = len(pubs)
    pubs_page, pagination = _paginate(pubs, request)

    return render_template(
        "publications.html",
        publications=pubs_page,
        total_count=total_count,
        pagination=pagination,
        sort_by=sort_by,
        sort_order=sort_order,
        base_args=_pagination_args(request),
    )


@app.route("/publications/add", methods=["GET", "POST"])
def add_publication():
    if not session.get("token"):
        return redirect(url_for("login"))

    if request.method == "POST":
        payload = {
            "title": request.form.get("title", ""),
            "year": _to_int_or_none(request.form.get("year")),
            "venue": request.form.get("venue") or None,
            "type": request.form.get("type") or None,
            "doi_link": request.form.get("doi_link") or None,
            "abstract": request.form.get("abstract") or None,

            "status": request.form.get("status", "draft"),
            "coauthor_ids": _parse_coauthor_ids(request.form.get("coauthor_ids", "")),
        }
        resp = requests.post(
            f"{BACKEND_URL}/publications", json=payload, headers=_auth_headers(), timeout=10
        )
        if resp.status_code == 401:
            session.clear()
            flash("Session expired. Please log in again.", "error")
            return redirect(url_for("login"))
        if resp.status_code != 201:
            detail = resp.json().get("detail", "Could not save publication.") if resp.content else "Could not save publication."
            flash(detail, "error")
            return redirect(url_for("add_publication"))

        publication = resp.json()

        # Optional file upload in the same submission
        file = request.files.get("file")
        if file and file.filename:
            files = {"file": (file.filename, file.stream, file.mimetype)}
            upload_resp = requests.post(
                f"{BACKEND_URL}/publications/{publication['id']}/upload",
                files=files,
                headers=_auth_headers(),
                timeout=30,
            )
            if upload_resp.status_code != 200:
                detail = (
                    upload_resp.json().get("detail", "File upload failed.")
                    if upload_resp.content
                    else "File upload failed."
                )
                flash(f"Publication saved, but file upload failed: {detail}", "error")
                return redirect(url_for("publications"))

        flash("Publication saved.", "success")
        return redirect(url_for("publications"))

    return render_template("publication_form.html", publication=None)


@app.route("/publications/<int:publication_id>/edit", methods=["GET", "POST"])
def edit_publication(publication_id):
    if not session.get("token"):
        return redirect(url_for("login"))

    if request.method == "POST":
        payload = {
            "title": request.form.get("title", ""),
            "year": _to_int_or_none(request.form.get("year")),
            "venue": request.form.get("venue") or None,
            "type": request.form.get("type") or None,
            "doi_link": request.form.get("doi_link") or None,
            "abstract": request.form.get("abstract") or None,
            "status": request.form.get("status", "draft"),
            "coauthor_ids": _parse_coauthor_ids(request.form.get("coauthor_ids", "")),
        }
        resp = requests.put(
            f"{BACKEND_URL}/publications/{publication_id}",
            json=payload,
            headers=_auth_headers(),
            timeout=10,
        )
        if resp.status_code == 401:
            session.clear()
            flash("Session expired. Please log in again.", "error")
            return redirect(url_for("login"))
        if resp.status_code != 200:
            detail = resp.json().get("detail", "Could not update publication.") if resp.content else "Could not update publication."
            flash(detail, "error")
            return redirect(url_for("edit_publication", publication_id=publication_id))

        flash("Publication updated.", "success")
        return redirect(url_for("publications"))

    resp = requests.get(f"{BACKEND_URL}/publications/{publication_id}", timeout=10)
    if resp.status_code != 200:
        flash("Publication not found.", "error")
        return redirect(url_for("publications"))

    publication = resp.json()
    researcher = _current_researcher()
    my_id = researcher.get("id") if researcher else None
    coauthor_ids = [a["researcher_id"] for a in publication.get("authors", []) if a["researcher_id"] != my_id]
    return render_template(
        "publication_form.html",
        publication=publication,
        existing_coauthor_ids=", ".join(str(i) for i in coauthor_ids),
    )

@app.route("/publications/<int:publication_id>/upload", methods=["POST"])
def upload_publication_file(publication_id):
    if not session.get("token"):
        return redirect(url_for("login"))

    file = request.files.get("file")
    if not file or file.filename == "":
        flash("Choose a file to upload.", "error")
        return redirect(url_for("edit_publication", publication_id=publication_id))

    files = {"file": (file.filename, file.stream, file.mimetype)}
    resp = requests.post(
        f"{BACKEND_URL}/publications/{publication_id}/upload",
        files=files,
        headers=_auth_headers(),
        timeout=30,
    )
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))
    if resp.status_code != 200:
        detail = resp.json().get("detail", "Upload failed.") if resp.content else "Upload failed."
        flash(detail, "error")
    else:
        flash("Publication file uploaded.", "success")
    return redirect(url_for("edit_publication", publication_id=publication_id))

@app.route("/publications/<int:publication_id>/delete", methods=["POST"])
def delete_publication(publication_id):
    if not session.get("token"):
        return redirect(url_for("login"))

    resp = requests.delete(
        f"{BACKEND_URL}/publications/{publication_id}", headers=_auth_headers(), timeout=10
    )
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))
    if resp.status_code != 204:
        flash("Could not delete publication.", "error")
    else:
        flash("Publication deleted.", "success")
    return redirect(url_for("publications"))

@app.route("/publications/review")
def review_queue():
    if not session.get("token"):
        return redirect(url_for("login"))

    if _current_role() not in ("reviewer", "system_admin"):
        flash("Only a Reviewer or System Admin can view the review queue.", "error")
        return redirect(url_for("dashboard"))

    resp = requests.get(
        f"{BACKEND_URL}/publications/pending-review", headers=_auth_headers(), timeout=10
    )
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))

    pubs = resp.json() if resp.status_code == 200 else []
    return render_template("review_queue.html", publications=pubs)


@app.route("/publications/reviewed")
def reviewed_publications():
    if not session.get("token"):
        return redirect(url_for("login"))
    if _current_role() not in ("reviewer", "system_admin"):
        flash("Only a Reviewer or System Admin can view this page.", "error")
        return redirect(url_for("dashboard"))

    decision = request.args.get("decision", "")
    params = {"decision": decision} if decision else {}
    resp = requests.get(
        f"{BACKEND_URL}/publications/reviewed-by-me", params=params, headers=_auth_headers(), timeout=10
    )
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))

    items = resp.json() if resp.status_code == 200 else []
    return render_template("reviewed_publications.html", items=items, decision=decision)
        

@app.route("/publications/<int:publication_id>/review", methods=["POST"])
def review_publication(publication_id):
    if not session.get("token"):
        return redirect(url_for("login"))

    payload = {
        "decision": request.form.get("decision"),
        "comment": request.form.get("comment") or None,
    }
    resp = requests.patch(
        f"{BACKEND_URL}/publications/{publication_id}/review",
        json=payload,
        headers=_auth_headers(),
        timeout=10,
    )
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))
    if resp.status_code != 200:
        detail = (
            resp.json().get("detail", "Could not submit review.")
            if resp.content
            else "Could not submit review."
        )
        flash(detail, "error")
    else:
        decision = payload["decision"]
        flash(
            "Publication approved and published."
            if decision == "approve"
            else "Publication sent back to draft.",
            "success",
        )
    return redirect(url_for("review_queue"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/conferences")
def conferences():
    if not session.get("token"):
        return redirect(url_for("login"))

    params = {}
    if request.args.get("q"):
        params["q"] = request.args["q"]
    if request.args.get("year"):
        params["year"] = request.args["year"]

    resp = requests.get(
        f"{BACKEND_URL}/conferences", params=params, headers=_auth_headers(), timeout=10
    )
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))

    conference_list = resp.json() if resp.status_code == 200 else []

    history_resp = requests.get(
        f"{BACKEND_URL}/conferences/me/history", headers=_auth_headers(), timeout=10
    )
    my_status_by_conference = {}
    if history_resp.status_code == 200:
        for item in history_resp.json():
            status_value = item["status"]
            my_status_by_conference[item["conference_id"]] = {
                "label": status_value.capitalize(),
                "css_class": STATUS_PILL_CLASS.get(status_value, "pill-teal"),
            }

    sort_by = request.args.get("sort_by", "start_date")
    sort_order = request.args.get("sort_order", "asc")
    allowed_sort_fields = {"name", "start_date", "end_date", "conference_type", "location"}
    if sort_by not in allowed_sort_fields:
        sort_by = "start_date"
    if sort_order not in {"asc", "desc"}:
        sort_order = "asc"

    conference_list = _sort_items(
        conference_list, sort_by, sort_order, allowed_sort_fields, "start_date"
    )
    total_count = len(conference_list)
    conferences_page, pagination = _paginate(conference_list, request)

    return render_template(
        "conferences.html",
        conferences=conferences_page,
        total_count=total_count,
        my_status_by_conference=my_status_by_conference,
        pagination=pagination,
        sort_by=sort_by,
        sort_order=sort_order,
        base_args=_pagination_args(request),
    )


@app.route("/conferences/add", methods=["GET", "POST"])
def add_conference():
    if not session.get("token"):
        return redirect(url_for("login"))

    my_institutions_resp = requests.get(
        f"{BACKEND_URL}/institutions/mine", headers=_auth_headers(), timeout=10
    )
    my_institutions = my_institutions_resp.json() if my_institutions_resp.status_code == 200 else []

    if request.method == "POST":
        payload = {
            "name": request.form.get("name", ""),
            "description": request.form.get("description") or None,
            "location": request.form.get("location") or None,
            "website_link": request.form.get("website_link") or None,
            "conference_type": request.form.get("conference_type") or None,
            "start_date": request.form.get("start_date"),
            "end_date": request.form.get("end_date") or None,
            "institution_id": _to_int_or_none(request.form.get("institution_id")),
        }
        resp = requests.post(
            f"{BACKEND_URL}/conferences", json=payload, headers=_auth_headers(), timeout=10
        )
        if resp.status_code == 401:
            session.clear()
            flash("Session expired. Please log in again.", "error")
            return redirect(url_for("login"))
        if resp.status_code != 201:
            detail = resp.json().get("detail", "Could not create conference.") if resp.content else "Could not create conference."
            flash(detail, "error")
            return redirect(url_for("add_conference"))

        flash("Conference created.", "success")
        return redirect(url_for("conferences"))

    return render_template("conference_form.html", my_institutions=my_institutions)

@app.route("/conferences/<int:conference_id>")
def conference_detail(conference_id):
    if not session.get("token"):
        return redirect(url_for("login"))

    conf_resp = requests.get(
        f"{BACKEND_URL}/conferences/{conference_id}", headers=_auth_headers(), timeout=10
    )
    if conf_resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))
    if conf_resp.status_code == 404:
        flash("Conference not found.", "error")
        return redirect(url_for("conference_detail", conference_id=conference_id))
    conference = conf_resp.json()

    sessions_resp = requests.get(
        f"{BACKEND_URL}/conferences/{conference_id}/sessions", headers=_auth_headers(), timeout=10
    )
    agenda = sessions_resp.json() if sessions_resp.status_code == 200 else []

    participants_resp = requests.get(
        f"{BACKEND_URL}/conferences/{conference_id}/participants",
        headers=_auth_headers(),
        timeout=10,
    )
    participants = participants_resp.json() if participants_resp.status_code == 200 else []

    history_resp = requests.get(
        f"{BACKEND_URL}/conferences/me/history", headers=_auth_headers(), timeout=10
    )
    registered = False
    my_status = None
    if history_resp.status_code == 200:
        for item in history_resp.json():
            if item["conference_id"] == conference_id:
                registered = True
                my_status = item["status"]
                break

    researcher = _current_researcher()
    my_researcher_id = researcher.get("id") if researcher else None
    my_user_id = researcher.get("user_id") if researcher else None
    current_role = _current_role()

    is_organizer = (
        my_user_id is not None
        and conference.get("created_by") is not None
        and my_user_id == conference.get("created_by")
    )
    if not is_organizer and current_role == "system_admin":
        is_organizer = True
    if not is_organizer and current_role == "institution_admin" and conference.get("institution_id"):
        mine_resp = requests.get(
            f"{BACKEND_URL}/institutions/mine", headers=_auth_headers(), timeout=10
        )
        if mine_resp.status_code == 200:
            my_institution_ids = {inst["id"] for inst in mine_resp.json()}
            is_organizer = conference.get("institution_id") in my_institution_ids

    return render_template(
        "conference_detail.html",
        conference=conference,
        agenda=agenda,
        participants=participants,
        registered=registered,
        my_status=my_status,
        conference_id=conference_id,
        my_researcher_id=my_researcher_id,
        is_organizer=is_organizer,
    )


@app.route("/conferences/<int:conference_id>/sessions", methods=["POST"])
def create_session(conference_id):
    if not session.get("token"):
        return redirect(url_for("login"))

    speaker_id = request.form.get("speaker_participation_id")
    payload = {
        "title": request.form.get("title", ""),
        "description": request.form.get("description") or None,
        "start_time": request.form.get("start_time"),
        "end_time": request.form.get("end_time") or None,
        "room": request.form.get("room") or None,
        "speaker_participation_id": int(speaker_id) if speaker_id else None,
    }
    resp = requests.post(
        f"{BACKEND_URL}/conferences/{conference_id}/sessions",
        json=payload,
        headers=_auth_headers(),
        timeout=10,
    )
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))
    if resp.status_code != 201:
        detail = resp.json().get("detail", "Could not add session.") if resp.content else "Could not add session."
        flash(detail, "error")
    else:
        flash("Session added to agenda.", "success")
    return redirect(url_for("conference_detail", conference_id=conference_id))

@app.route("/conferences/<int:conference_id>/register", methods=["POST"])
def register_conference(conference_id):
    if not session.get("token"):
        return redirect(url_for("login"))

    payload = {
        "role": request.form.get("role", "attendee"),
        "presentation_title": request.form.get("presentation_title") or None,
    }
    resp = requests.post(
        f"{BACKEND_URL}/conferences/{conference_id}/register",
        json=payload,
        headers=_auth_headers(),
        timeout=10,
    )
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))
    if resp.status_code != 201:
        detail = resp.json().get("detail", "Could not register.") if resp.content else "Could not register."
        flash(detail, "error")
    else:
        flash("Registered for the conference.", "success")
    return redirect(url_for("conferences"))


@app.route("/conferences/participations/<int:participation_id>/status", methods=["POST"])
def update_participation_status(participation_id):
    if not session.get("token"):
        return redirect(url_for("login"))

    new_status = request.form.get("status", "")
    resp = requests.patch(
        f"{BACKEND_URL}/conferences/participations/{participation_id}/status",
        json={"status": new_status},
        headers=_auth_headers(),
        timeout=10,
    )
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))
    if resp.status_code != 200:
        detail = resp.json().get("detail", "Could not update status.") if resp.content else "Could not update status."
        flash(detail, "error")
    else:
        flash(f"Status updated to {new_status}.", "success")
    return redirect(request.referrer or url_for("conferences"))


@app.route("/conferences/participations/<int:participation_id>/role", methods=["POST"])
def update_participation_role(participation_id):
    if not session.get("token"):
        return redirect(url_for("login"))

    new_role = request.form.get("role", "")
    resp = requests.patch(
        f"{BACKEND_URL}/conferences/participations/{participation_id}/role",
        json={"role": new_role},
        headers=_auth_headers(),
        timeout=10,
    )
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))
    if resp.status_code != 200:
        detail = resp.json().get("detail", "Could not update role.") if resp.content else "Could not update role."
        flash(detail, "error")
    else:
        flash(f"Role updated to {new_role}.", "success")
    return redirect(request.referrer or url_for("conferences"))


@app.route("/conferences/participations/<int:participation_id>/upload", methods=["POST"])
def upload_presentation(participation_id):
    if not session.get("token"):
        return redirect(url_for("login"))

    file = request.files.get("file")
    if not file or file.filename == "":
        flash("Choose a file to upload.", "error")
        return redirect(url_for("conference_history"))

    files = {"file": (file.filename, file.stream, file.mimetype)}
    resp = requests.post(
        f"{BACKEND_URL}/conferences/participations/{participation_id}/upload",
        files=files,
        headers=_auth_headers(),
        timeout=30,
    )
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))
    if resp.status_code != 200:
        detail = resp.json().get("detail", "Upload failed.") if resp.content else "Upload failed."
        flash(detail, "error")
    else:
        flash("Presentation file uploaded.", "success")
    return redirect(url_for("conference_history"))


@app.route("/conferences/history")
def conference_history():
    if not session.get("token"):
        return redirect(url_for("login"))

    resp = requests.get(
        f"{BACKEND_URL}/conferences/me/history", headers=_auth_headers(), timeout=10
    )
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))

    history = resp.json() if resp.status_code == 200 else []
    for item in history:
        if item.get("file_url"):
            item["file_url"] = f"{BACKEND_URL}{item['file_url']}"
    return render_template("conference_history.html", history=history)


def _safe_count(url):
    try:
        r = requests.get(url, headers=_auth_headers(), timeout=10)
        return len(r.json()) if r.status_code == 200 else None
    except requests.RequestException:
        return None


def _admin_user_stats():
    """Fetch the full user list plus role/activity/system counts used by
    both the System Admin dashboard summary and the full user-management
    page. Returns (users, stats) or ([], None) if the call fails."""
    resp = requests.get(f"{BACKEND_URL}/admin/users", headers=_auth_headers(), timeout=10)
    if resp.status_code != 200:
        return [], None

    users = resp.json()
    for u in users:
        u["role_label"] = ROLE_LABEL.get(u.get("role"), u.get("role"))
        u["role_pill_class"] = ROLE_PILL_CLASS.get(u.get("role"), "pill-gray")

    role_counts = {"researcher": 0, "institution_admin": 0, "reviewer": 0, "system_admin": 0}
    active_count = 0
    for u in users:
        role_counts[u.get("role")] = role_counts.get(u.get("role"), 0) + 1
        if u.get("is_active"):
            active_count += 1

    stats = {
        "total_users": len(users),
        "active_users": active_count,
        "inactive_users": len(users) - active_count,
        "role_counts": role_counts,
        "total_institutions": _safe_count(f"{BACKEND_URL}/institutions/"),
        "total_conferences": _safe_count(f"{BACKEND_URL}/conferences"),
        "total_publications": _safe_count(f"{BACKEND_URL}/publications"),
    }
    return users, stats


@app.route("/admin/users")
def admin_users():
    if not session.get("token"):
        return redirect(url_for("login"))

    if _current_role() != "system_admin":
        flash("Only a System Admin can view this page.", "error")
        return redirect(url_for("dashboard"))

    users, stats = _admin_user_stats()
    if stats is None:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))

    return render_template("admin_users.html", users=users, stats=stats)


@app.route("/admin/users/<int:user_id>/update", methods=["POST"])
def admin_update_user(user_id):
    if not session.get("token"):
        return redirect(url_for("login"))

    payload = {}
    new_role = request.form.get("role")
    if new_role:
        payload["role"] = new_role
    new_active = request.form.get("is_active")
    if new_active is not None:
        payload["is_active"] = new_active == "true"

    resp = requests.patch(
        f"{BACKEND_URL}/admin/users/{user_id}",
        json=payload,
        headers=_auth_headers(),
        timeout=10,
    )
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))
    if resp.status_code != 200:
        detail = resp.json().get("detail", "Could not update user.") if resp.content else "Could not update user."
        flash(detail, "error")
    else:
        flash("User updated.", "success")
    return redirect(url_for("admin_users"))


@app.route("/admin/reviewer-assignments")
def assign_reviewers():
    if not session.get("token"):
        return redirect(url_for("login"))
    if _current_role() != "system_admin":
        flash("Only a System Admin can view this page.", "error")
        return redirect(url_for("dashboard"))

    def _get(path):
        resp = requests.get(f"{BACKEND_URL}{path}", headers=_auth_headers(), timeout=10)
        return resp.json() if resp.status_code == 200 else None

    all_users = _get("/admin/users") or []
    reviewers = [u for u in all_users if u["role"] == "reviewer"]
    institutions = _get("/institutions/") or []
    all_publications = _get("/publications") or []
    submitted_publications = [p for p in all_publications if p.get("status") == "submitted"]
    assignments = _get("/reviewer-assignments") or []

    reviewer_lookup = {u["id"]: u["email"] for u in all_users}
    institution_lookup = {i["id"]: i["name"] for i in institutions}
    publication_lookup = {p["id"]: p["title"] for p in all_publications}
    for a in assignments:
        a["reviewer_email"] = reviewer_lookup.get(a["reviewer_user_id"], f"User #{a['reviewer_user_id']}")
        a["institution_name"] = institution_lookup.get(a["institution_id"]) if a["institution_id"] else None
        a["publication_title"] = publication_lookup.get(a["publication_id"]) if a["publication_id"] else None

    return render_template(
        "assign_reviewers.html",
        reviewers=reviewers,
        institutions=institutions,
        submitted_publications=submitted_publications,
        assignments=assignments,
    )


@app.route("/admin/reviewer-assignments/create", methods=["POST"])
def create_reviewer_assignment():
    if not session.get("token"):
        return redirect(url_for("login"))

    scope = request.form.get("scope")
    payload = {"reviewer_user_id": _to_int_or_none(request.form.get("reviewer_user_id"))}
    if scope == "institution":
        payload["institution_id"] = _to_int_or_none(request.form.get("institution_id"))
    else:
        payload["publication_id"] = _to_int_or_none(request.form.get("publication_id"))

    resp = requests.post(
        f"{BACKEND_URL}/reviewer-assignments", json=payload, headers=_auth_headers(), timeout=10
    )
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))
    if resp.status_code != 201:
        detail = resp.json().get("detail", "Could not create assignment.") if resp.content else "Could not create assignment."
        flash(detail, "error")
    else:
        flash("Reviewer assigned.", "success")
    return redirect(url_for("assign_reviewers"))


@app.route("/admin/reviewer-assignments/<int:assignment_id>/delete", methods=["POST"])
def delete_reviewer_assignment(assignment_id):
    if not session.get("token"):
        return redirect(url_for("login"))

    resp = requests.delete(
        f"{BACKEND_URL}/reviewer-assignments/{assignment_id}", headers=_auth_headers(), timeout=10
    )
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))
    if resp.status_code != 204:
        detail = resp.json().get("detail", "Could not remove assignment.") if resp.content else "Could not remove assignment."
        flash(detail, "error")
    else:
        flash("Assignment removed.", "success")
    return redirect(url_for("assign_reviewers"))


# reports
@app.route("/reports")
def reports():
    if not session.get("token"):
        return redirect(url_for("login"))

    headers = _auth_headers()

    dashboard = requests.get(f"{BACKEND_URL}/reports/dashboard", headers=headers).json()
    institution_report = requests.get(f"{BACKEND_URL}/reports/institutions", headers=headers).json()
    publication_year = requests.get(f"{BACKEND_URL}/reports/publications/year", headers=headers).json()
    publication_type = requests.get(f"{BACKEND_URL}/reports/publications/type", headers=headers).json()
    publication_status = requests.get(f"{BACKEND_URL}/reports/publications/status", headers=headers).json()
    conference_type = requests.get(f"{BACKEND_URL}/reports/conferences/type", headers=headers).json()
    user_roles = requests.get(f"{BACKEND_URL}/reports/users/roles", headers=headers).json()
    departments = requests.get(f"{BACKEND_URL}/reports/departments", headers=headers).json()
    interests = requests.get(f"{BACKEND_URL}/reports/research-interests", headers=headers).json()
    skills = requests.get(f"{BACKEND_URL}/reports/skills", headers=headers).json()
    collaboration_status = requests.get(f"{BACKEND_URL}/reports/collaborations/status", headers=headers).json()
    top_collaborations = requests.get(f"{BACKEND_URL}/reports/collaborations/top", headers=headers).json()
    top_cited_papers = requests.get(f"{BACKEND_URL}/reports/citations/top-papers", headers=headers).json()
    influential_papers = requests.get(f"{BACKEND_URL}/reports/citations/influential-papers", headers=headers).json()
    top_cited_researchers = requests.get(f"{BACKEND_URL}/reports/citations/top-researchers", headers=headers).json()
    top_cited_institutions = requests.get(f"{BACKEND_URL}/reports/citations/top-institutions", headers=headers).json()

    return render_template(
        "reports.html",
        dashboard=dashboard,
        institution_report=institution_report,
        publication_year=publication_year,
        publication_type=publication_type,
        publication_status=publication_status,
        conference_type=conference_type,
        user_roles=user_roles,
        departments=departments,
        interests=interests,
        skills=skills,
        collaboration_status=collaboration_status,
        top_collaborations=top_collaborations,
        top_cited_papers=top_cited_papers,
        influential_papers=influential_papers,
        top_cited_researchers=top_cited_researchers,
        top_cited_institutions=top_cited_institutions,
    )


@app.route("/reports/download/excel")
def download_report_excel():
    if not session.get("token"):
        return redirect(url_for("login"))
    resp = requests.get(f"{BACKEND_URL}/reports/dashboard/excel", headers=_auth_headers())
    return Response(
        resp.content,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment;filename=dashboard_report.xlsx"},
    )


@app.route("/reports/download/pdf")
def download_report_pdf():
    if not session.get("token"):
        return redirect(url_for("login"))
    resp = requests.get(f"{BACKEND_URL}/reports/dashboard/pdf", headers=_auth_headers())
    return Response(
        resp.content,
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment;filename=dashboard_report.pdf"},
    )


@app.route("/reports/download/compliance/excel")
def download_compliance_excel():
    if not session.get("token"):
        return redirect(url_for("login"))
    resp = requests.get(f"{BACKEND_URL}/reports/compliance/excel", headers=_auth_headers())
    if resp.status_code == 403:
        flash("Only a System Admin can export the compliance report.", "error")
        return redirect(url_for("reports"))
    return Response(
        resp.content,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment;filename=compliance_report.xlsx"},
    )


@app.route("/reports/download/compliance/pdf")
def download_compliance_pdf():
    if not session.get("token"):
        return redirect(url_for("login"))
    resp = requests.get(f"{BACKEND_URL}/reports/compliance/pdf", headers=_auth_headers())
    if resp.status_code == 403:
        flash("Only a System Admin can export the compliance report.", "error")
        return redirect(url_for("reports"))
    return Response(
        resp.content,
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment;filename=compliance_report.pdf"},
    )

@app.route("/citations", methods=["GET", "POST"])
def citations():
    if not session.get("token"):
        return redirect(url_for("login"))

    researcher = _current_researcher()
    researcher_id = researcher.get("id") if researcher else None

    if request.method == "POST":
        if not researcher_id:
            flash("Create your researcher profile before managing citations.", "error")
            return redirect(url_for("citations"))

        cited_publication_id = _to_int_or_none(request.form.get("cited_publication_id"))
        payload = {
            "citing_publication_id": _to_int_or_none(request.form.get("citing_publication_id")),
            "cited_publication_id": cited_publication_id,
        }
        if cited_publication_id is None:
            payload["cited_title"] = request.form.get("cited_title") or None
            payload["cited_authors"] = request.form.get("cited_authors") or None
            payload["cited_year"] = _to_int_or_none(request.form.get("cited_year"))
            payload["cited_venue"] = request.form.get("cited_venue") or None

        resp = requests.post(
            f"{BACKEND_URL}/citations", json=payload, headers=_auth_headers(), timeout=10
        )
        if resp.status_code == 401:
            session.clear()
            flash("Session expired. Please log in again.", "error")
            return redirect(url_for("login"))
        if resp.status_code != 201:
            detail = (
                resp.json().get("detail", "Could not add citation.")
                if resp.content
                else "Could not add citation."
            )
            flash(detail, "error")
        else:
            flash("Citation added.", "success")
        return redirect(url_for("citations"))

    my_publications = []
    all_publications = []
    my_citations = []
    if researcher_id:
        my_pubs_resp = requests.get(
            f"{BACKEND_URL}/publications", params={"author_id": researcher_id}, timeout=10
        )
        my_publications = my_pubs_resp.json() if my_pubs_resp.status_code == 200 else []

        all_pubs_resp = requests.get(f"{BACKEND_URL}/publications", timeout=10)
        all_publications = all_pubs_resp.json() if all_pubs_resp.status_code == 200 else []

        for pub in my_publications:
            c_resp = requests.get(
                f"{BACKEND_URL}/citations",
                params={"citing_publication_id": pub["id"]},
                timeout=10,
            )
            if c_resp.status_code == 200:
                my_citations.extend(c_resp.json())
        my_citations.sort(key=lambda c: c["created_at"], reverse=True)
    else:
        flash("Create your researcher profile before managing citations.", "error")

    return render_template(
        "citations.html",
        my_publications=my_publications,
        all_publications=all_publications,
        my_citations=my_citations,
    )


@app.route("/citations/<int:citation_id>/delete", methods=["POST"])
def delete_citation(citation_id):
    if not session.get("token"):
        return redirect(url_for("login"))

    resp = requests.delete(
        f"{BACKEND_URL}/citations/{citation_id}", headers=_auth_headers(), timeout=10
    )
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))
    if resp.status_code != 204:
        detail = (
            resp.json().get("detail", "Could not delete citation.")
            if resp.content
            else "Could not delete citation."
        )
        flash(detail, "error")
    else:
        flash("Citation deleted.", "success")
    return redirect(url_for("citations"))


@app.route("/citations/insights")
def citation_insights():
    if not session.get("token"):
        return redirect(url_for("login"))

    def _get(path):
        resp = requests.get(f"{BACKEND_URL}{path}", headers=_auth_headers(), timeout=10)
        return resp.json() if resp.status_code == 200 else None

    top_papers = _get("/citations/stats/top-papers") or []
    top_authors = _get("/citations/stats/top-authors") or []
    top_institutions = _get("/citations/stats/top-institutions") or []
    network = _get("/citations/network") or {"nodes": [], "edges": []}

    return render_template(
        "citation_insights.html",
        top_papers=top_papers,
        top_authors=top_authors,
        top_institutions=top_institutions,
        network=network,
    )

@app.route("/collaborations")
def collaborations():
    if not session.get("token"):
        return redirect(url_for("login"))

    def _get(path, params=None):
        resp = requests.get(f"{BACKEND_URL}{path}", params=params, headers=_auth_headers(), timeout=10)
        return resp

    incoming_resp = _get("/collaborations/collaboration-requests", {"direction": "incoming", "status": "pending"})
    outgoing_resp = _get("/collaborations/collaboration-requests", {"direction": "outgoing", "status": "pending"})
    my_collabs_resp = _get("/collaborations/my", {"page": 1, "page_size": 25})

    for resp in (incoming_resp, outgoing_resp, my_collabs_resp):
        if resp.status_code == 401:
            session.clear()
            flash("Session expired. Please log in again.", "error")
            return redirect(url_for("login"))
        if resp.status_code != 200:
            try:
                detail = resp.json().get("detail", "Something went wrong.")
            except ValueError:
                detail = f"Backend error {resp.status_code}: {resp.text[:200]}"
            flash(detail, "error")
            return redirect(url_for("dashboard"))

    incoming = incoming_resp.json()
    outgoing = outgoing_resp.json()
    my_collabs = my_collabs_resp.json()

    q = request.args.get("q", "").strip()
    directory_results = []
    if q:
        search_resp = requests.get(
            f"{BACKEND_URL}/researchers/search", params={"q": q}, headers=_auth_headers(), timeout=10
        )
        if search_resp.status_code == 200:
            directory_results = search_resp.json()

    researcher = _current_researcher()
    if researcher:
        my_researcher_id = researcher.get("id")
        directory_results = [r for r in directory_results if r.get("id") != my_researcher_id]

    return render_template(
        "collaborations.html",
        incoming_requests=incoming["items"],
        outgoing_requests=outgoing["items"],
        my_collaborations=my_collabs["items"],
        directory_results=directory_results,
        q=q,
    )


@app.route("/collaborations/send", methods=["POST"])
def send_collaboration_request():
    if not session.get("token"):
        return redirect(url_for("login"))

    payload = {
        "addressee_researcher_id": _to_int_or_none(request.form.get("addressee_researcher_id")),
        "message": request.form.get("message") or None,
    }
    resp = requests.post(
        f"{BACKEND_URL}/collaborations/collaboration-requests", json=payload, headers=_auth_headers(), timeout=10
    )
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))
    if resp.status_code != 201:
        detail = resp.json().get("detail", "Could not send request.") if resp.content else "Could not send request."
        flash(detail, "error")
    else:
        flash("Collaboration request sent.", "success")
    return redirect(request.referrer or url_for("collaborations"))


@app.route("/collaborations/requests/<int:request_id>/respond", methods=["POST"])
def respond_collaboration_request(request_id):
    if not session.get("token"):
        return redirect(url_for("login"))

    action = request.form.get("action", "")
    status_map = {"accept": "accepted", "reject": "rejected", "cancel": "cancelled"}
    new_status = status_map.get(action)
    if new_status is None:
        flash("Unknown action.", "error")
        return redirect(url_for("collaborations"))

    resp = requests.patch(
        f"{BACKEND_URL}/collaborations/collaboration-requests/{request_id}",
        json={"status": new_status},
        headers=_auth_headers(),
        timeout=10,
    )
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))
    if resp.status_code != 200:
        detail = resp.json().get("detail", "Could not update request.") if resp.content else "Could not update request."
        flash(detail, "error")
    else:
        flash_text = {
            "accepted": "Request accepted -- you're now collaborators.",
            "rejected": "Request rejected.",
            "cancelled": "Request cancelled.",
        }[new_status]
        flash(flash_text, "success")
    return redirect(url_for("collaborations"))


@app.route("/collaborations/<int:collaboration_id>")
def collaboration_detail(collaboration_id):
    if not session.get("token"):
        return redirect(url_for("login"))

    resp = requests.get(f"{BACKEND_URL}/collaborations/{collaboration_id}", headers=_auth_headers(), timeout=10)
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))
    if resp.status_code == 403:
        flash("You can only view collaborations you're part of.", "error")
        return redirect(url_for("collaborations"))
    if resp.status_code != 200:
        flash("Collaboration not found.", "error")
        return redirect(url_for("collaborations"))

    return render_template("collaboration_detail.html", collaboration=resp.json())


@app.route("/collaborations/network")
def collaboration_network():
    if not session.get("token"):
        return redirect(url_for("login"))

    try:
        depth = int(request.args.get("depth", 2))
    except ValueError:
        depth = 2
    depth = max(1, min(depth, 3))

    resp = requests.get(
        f"{BACKEND_URL}/collaborations/network", params={"depth": depth}, headers=_auth_headers(), timeout=10
    )
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))

    network = resp.json() if resp.status_code == 200 else {"nodes": [], "edges": []}
    return render_template("collaboration_network.html", network=network, depth=depth)


@app.route("/collaborations/suggested")
def suggested_collaborators():
    if not session.get("token"):
        return redirect(url_for("login"))

    resp = requests.get(
        f"{BACKEND_URL}/collaborations/suggested", params={"limit": 12}, headers=_auth_headers(), timeout=10
    )
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))

    suggestions = resp.json() if resp.status_code == 200 else []
    return render_template("suggested_collaborators.html", suggestions=suggestions)


# projects
@app.route("/projects")
def projects():
    if not session.get("token"):
        return redirect(url_for("login"))

    resp = requests.get(f"{BACKEND_URL}/projects", headers=_auth_headers(), timeout=10)
    if resp.status_code != 200:
        flash("Could not load projects.", "error")
        my_projects = []
    else:
        my_projects = resp.json()

    return render_template("projects.html", projects=my_projects)


@app.route("/projects/new", methods=["GET", "POST"])
def new_project():
    if not session.get("token"):
        return redirect(url_for("login"))

    if request.method == "POST":
        payload = {
            "title": request.form.get("title", "").strip(),
            "description": request.form.get("description", "").strip() or None,
            "start_date": request.form.get("start_date") or None,
            "end_date": request.form.get("end_date") or None,
        }
        resp = requests.post(f"{BACKEND_URL}/projects", json=payload, headers=_auth_headers(), timeout=10)
        if resp.status_code != 201:
            detail = resp.json().get("detail", "Could not create project.") if resp.content else "Could not create project."
            flash(detail, "error")
            return render_template("new_project.html", form=request.form)

        flash("Project created.", "success")
        return redirect(url_for("project_detail", project_id=resp.json()["id"]))

    return render_template("new_project.html", form={})


@app.route("/projects/<int:project_id>")
def project_detail(project_id):
    if not session.get("token"):
        return redirect(url_for("login"))

    resp = requests.get(f"{BACKEND_URL}/projects/{project_id}", headers=_auth_headers(), timeout=10)
    if resp.status_code == 404:
        flash("Project not found.", "error")
        return redirect(url_for("projects"))
    if resp.status_code == 403:
        flash("You are not a member of this project.", "error")
        return redirect(url_for("projects"))

    project = resp.json()
    researcher = _current_researcher()
    is_lead = researcher and researcher.get("id") == project.get("lead_researcher_id")

    q = request.args.get("q", "").strip()
    search_results = []
    if q and is_lead:
        search_resp = requests.get(
            f"{BACKEND_URL}/researchers/search", params={"q": q}, headers=_auth_headers(), timeout=10
        )
        if search_resp.status_code == 200:
            member_ids = {m["researcher_id"] for m in project.get("members", [])}
            search_results = [r for r in search_resp.json() if r["id"] not in member_ids]

    return render_template(
        "project_detail.html",
        project=project,
        is_lead=is_lead,
        my_researcher_id=researcher.get("id") if researcher else None,
        q=q,
        search_results=search_results,
    )


@app.route("/projects/<int:project_id>/members/invite", methods=["POST"])
def invite_project_member(project_id):
    if not session.get("token"):
        return redirect(url_for("login"))

    researcher_id = request.form.get("researcher_id")
    resp = requests.post(
        f"{BACKEND_URL}/projects/{project_id}/members",
        json={"researcher_id": int(researcher_id)},
        headers=_auth_headers(),
        timeout=10,
    )
    if resp.status_code != 201:
        detail = resp.json().get("detail", "Could not invite member.") if resp.content else "Could not invite member."
        flash(detail, "error")
    else:
        flash("Invite sent.", "success")

    return redirect(url_for("project_detail", project_id=project_id))


@app.route("/projects/<int:project_id>/members/<int:member_id>/respond", methods=["POST"])
def respond_project_invite(project_id, member_id):
    if not session.get("token"):
        return redirect(url_for("login"))

    accept = request.form.get("accept") == "1"
    resp = requests.post(
        f"{BACKEND_URL}/projects/{project_id}/members/{member_id}/respond",
        json={"accept": accept},
        headers=_auth_headers(),
        timeout=10,
    )
    if resp.status_code != 200:
        flash("Could not respond to invite.", "error")
    else:
        flash("Invite accepted." if accept else "Invite declined.", "success")

    return redirect(url_for("project_detail", project_id=project_id))


@app.route("/projects/<int:project_id>/members/<int:member_id>/remove", methods=["POST"])
def remove_project_member(project_id, member_id):
    if not session.get("token"):
        return redirect(url_for("login"))

    resp = requests.delete(
        f"{BACKEND_URL}/projects/{project_id}/members/{member_id}", headers=_auth_headers(), timeout=10
    )
    if resp.status_code != 204:
        flash("Could not remove member.", "error")
    else:
        flash("Member removed.", "success")

    return redirect(url_for("project_detail", project_id=project_id))


@app.route("/notifications")
def notifications():
    if not session.get("token"):
        return redirect(url_for("login"))

    resp = requests.get(f"{BACKEND_URL}/notifications", headers=_auth_headers(), timeout=10)
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))
    if resp.status_code != 200:
        flash("Could not load notifications.", "error")
        return render_template("notifications.html", items=[])

    data = resp.json()
    return render_template("notifications.html", items=data["items"])

@app.route("/notifications/preview.json")
def notifications_preview():
    if not session.get("token"):
        return jsonify({"items": [], "unread_count": 0})

    resp = requests.get(f"{BACKEND_URL}/notifications", params={"limit": 6}, headers=_auth_headers(), timeout=10)
    if resp.status_code != 200:
        return jsonify({"items": [], "unread_count": 0})

    data = resp.json()
    return jsonify({"items": data["items"], "unread_count": data["unread_count"]})

@app.route("/notifications/<int:notification_id>/read", methods=["POST"])
def mark_notification_read(notification_id):
    if not session.get("token"):
        return redirect(url_for("login"))

    resp = requests.patch(
        f"{BACKEND_URL}/notifications/{notification_id}/read", headers=_auth_headers(), timeout=10
    )
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))

    # Support both: clicking a notification's own "mark read" button (stays
    # on the page) and clicking the notification to jump to its link.
    next_url = request.form.get("next")
    if next_url:
        return redirect(next_url)
    return redirect(url_for("notifications"))


@app.route("/notifications/mark-all-read", methods=["POST"])
def mark_all_notifications_read():
    if not session.get("token"):
        return redirect(url_for("login"))

    resp = requests.post(
        f"{BACKEND_URL}/notifications/mark-all-read", headers=_auth_headers(), timeout=10
    )
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))

    flash("All notifications marked as read.", "success")
    return redirect(url_for("notifications"))
    

@app.route("/verify-email")
def verify_email():
    token = request.args.get("token", "")
    if not token:
        flash("Missing verification token.", "error")
        return redirect(url_for("login"))

    resp = requests.post(f"{BACKEND_URL}/auth/verify-email", json={"token": token}, timeout=10)
    if resp.status_code == 200:
        flash("Email verified! You can now log in.", "success")
    else:
        detail = resp.json().get("detail", "Verification failed.") if resp.content else "Verification failed."
        flash(detail, "error")

    return redirect(url_for("login"))


@app.route("/resend-verification", methods=["POST"])
def resend_verification():
    email = request.form.get("email", "").strip()
    if email:
        requests.post(f"{BACKEND_URL}/auth/resend-verification", json={"email": email}, timeout=10)
    flash("If that account exists and isn't verified yet, a new link has been sent.", "success")
    return redirect(url_for("login"))


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        if _honeypot_tripped():
            flash("If that email is registered, a reset link has been sent.", "success")
            return redirect(url_for("login"))
        if not _verify_recaptcha(request.form.get("g-recaptcha-response", "")):
            flash("Please complete the CAPTCHA verification.", "error")
            return redirect(url_for("forgot_password"))
        email = request.form.get("email", "").strip()
        requests.post(f"{BACKEND_URL}/auth/forgot-password", json={"email": email}, timeout=10)
        flash("If that email is registered, a reset link has been sent.", "success")
        return redirect(url_for("login"))

    return render_template("forgot_password.html", recaptcha_site_key=RECAPTCHA_SITE_KEY)


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    token = request.args.get("token", "") if request.method == "GET" else request.form.get("token", "")

    if request.method == "POST":
        new_password = request.form.get("password", "")
        resp = requests.post(
            f"{BACKEND_URL}/auth/reset-password",
            json={"token": token, "new_password": new_password},
            timeout=10,
        )
        if resp.status_code == 200:
            flash("Password updated. Please log in.", "success")
            return redirect(url_for("login"))

        detail = resp.json().get("detail", "Could not reset password.") if resp.content else "Could not reset password."
        flash(detail, "error")
        return render_template("reset_password.html", token=token)

    if not token:
        flash("Missing reset token.", "error")
        return redirect(url_for("login"))

    return render_template("reset_password.html", token=token)


@app.route("/audit")
def audit_log():
    if not session.get("token"):
        return redirect(url_for("login"))
    if _current_role() != "system_admin":
        flash("Only a System Admin can view the audit log.", "error")
        return redirect(url_for("dashboard"))

    action = request.args.get("action", "").strip()
    entity_type = request.args.get("entity_type", "").strip()
    user_id = request.args.get("user_id", type=int)
    date_from = request.args.get("date_from", "").strip()
    date_to = request.args.get("date_to", "").strip()
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 25, type=int)

    params = {"page": page, "page_size": page_size if page_size in {10, 25, 50, 100} else 25}
    if action:
        params["action"] = action
    if entity_type:
        params["entity_type"] = entity_type
    if user_id is not None:
        params["user_id"] = user_id
    if date_from:
        params["date_from"] = date_from
    if date_to:
        params["date_to"] = date_to

    resp = requests.get(f"{BACKEND_URL}/audit-logs", params=params, headers=_auth_headers(), timeout=10)
    if resp.status_code == 403:
        flash("Only a System Admin can view the audit log.", "error")
        return redirect(url_for("dashboard"))

    data = resp.json() if resp.status_code == 200 else {"items": [], "total": 0, "page": 1, "page_size": 25}

    actions_resp = requests.get(f"{BACKEND_URL}/audit-logs/actions", headers=_auth_headers(), timeout=10)
    actions = actions_resp.json() if actions_resp.status_code == 200 else []

    logs = []
    for log in data.get("items", []):
        logs.append({
            "id": log.get("id"),
            "user_id": log.get("actor_user_id"),
            "user_email": log.get("actor_email"),
            "action": log.get("action"),
            "entity_type": log.get("entity_type"),
            "entity_id": log.get("entity_id"),
            "details": log.get("details"),
            "created_at": log.get("created_at"),
        })

    pagination = {
        "total": data.get("total", 0),
        "page": data.get("page", 1),
        "per_page": data.get("page_size", 25),
    }

    return render_template(
        "audit.html",
        logs=logs,
        actions=actions,
        pagination=pagination,
        request=request,
    )


@app.route("/admin/audit-logs")
def audit_logs():
    return audit_log()

@app.route("/auth/google", methods=["POST"])
def auth_google():
    credential = request.form.get("credential", "")
    role = request.form.get("role") or None
    institution_id = _to_int_or_none(request.form.get("institution_id"))

    payload = {"id_token": credential}
    if role:
        payload["role"] = role
    if institution_id:
        payload["institution_id"] = institution_id

    try:
        resp = requests.post(f"{BACKEND_URL}/auth/google", json=payload, timeout=10)
    except requests.RequestException:
        flash("Could not reach the backend.", "error")
        return redirect(url_for("login"))

    if resp.status_code != 200:
        detail = resp.json().get("detail", "Google sign-in failed.") if resp.content else "Google sign-in failed."
        flash(detail, "error")
        return redirect(url_for("login"))

    data = resp.json()

    if data.get("pending_approval"):
        flash(data.get("message", "Application submitted, awaiting approval."), "success")
        return redirect(url_for("login"))

    if data.get("needs_role_selection"):
        flash("No account found for that Google email. Please use Register instead.", "error")
        return redirect(url_for("register"))

    session["token"] = data["access_token"]
    flash("Logged in successfully.", "success")
    return redirect(url_for("dashboard"))


@app.route("/messages")
def messages_inbox():
    if "token" not in session:
        return redirect(url_for("login"))
    resp = requests.get(f"{BACKEND_URL}/messages/inbox", headers=_auth_headers(), timeout=10)
    items = resp.json().get("items", []) if resp.status_code == 200 else []
    return render_template("messages_inbox.html", items=items)


def _message_thread(scope_type, scope_id):
    if "token" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        body = request.form.get("body", "").strip()
        if body:
            requests.post(
                f"{BACKEND_URL}/messages/{scope_type}/{scope_id}",
                json={"body": body},
                headers=_auth_headers(),
                timeout=10,
            )
        return redirect(url_for("project_messages" if scope_type == "project" else "collaboration_messages", **{f"{scope_type}_id": scope_id}))

    resp = requests.get(f"{BACKEND_URL}/messages/{scope_type}/{scope_id}", headers=_auth_headers(), timeout=10)
    if resp.status_code != 200:
        flash(resp.json().get("detail", "Could not load this conversation."), "error")
        return redirect(url_for("messages_inbox"))
    return render_template("message_thread.html", conversation=resp.json())


@app.route("/projects/<int:project_id>/messages", methods=["GET", "POST"])
def project_messages(project_id):
    return _message_thread("project", project_id)


@app.route("/collaborations/<int:collaboration_id>/messages", methods=["GET", "POST"])
def collaboration_messages(collaboration_id):
    return _message_thread("collaboration", collaboration_id)

if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", debug=debug_mode, port=5000)
