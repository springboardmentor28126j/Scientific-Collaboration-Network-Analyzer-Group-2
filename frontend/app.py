"""
Flask frontend for the Scientific Collaboration Network Analyzer (Milestone 1).

Wired to the FastAPI backend: login/register/profile now call the real API
and store the JWT access token in the Flask session.
"""
import os

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash, g, Response
import requests

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")

BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")

# reCAPTCHA v2 checkbox on /login. This is Google's official public TEST
# site key -- always passes, works on any host including localhost.
# Replace with your own site key from google.com/recaptcha/admin before
# a real deployment (must match the RECAPTCHA_SECRET_KEY the backend
# verifies against -- see backend/.env.example).
RECAPTCHA_SITE_KEY = os.environ.get("RECAPTCHA_SITE_KEY", "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI")


def _auth_headers() -> dict:
    token = session.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}


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
    """Cheap, best-effort unread count for the nav bell badge. Never
    raises or logs the user out on failure -- a notification hiccup
    shouldn't break every other page in the app."""
    if not session.get("token"):
        return 0
    if not hasattr(g, "_unread_notification_cache"):
        try:
            resp = requests.get(
                f"{BACKEND_URL}/notifications/unread-count",
                headers=_auth_headers(),
                timeout=10,
            )
            g._unread_notification_cache = (
                resp.json().get("unread_count", 0) if resp.status_code == 200 else 0
            )
        except requests.RequestException:
            g._unread_notification_cache = 0
    return g._unread_notification_cache


@app.context_processor
def inject_role():
    return {
        "current_role": _current_role(),
        "current_user_id": _current_user_id(),
        "unread_notification_count": _unread_notification_count(),
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

PROJECT_STATUS_PILL_CLASS = {
    "planned": "pill-blue",
    "ongoing": "pill-teal",
    "completed": "pill-purple",
    "cancelled": "pill-gray",
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


def _server_pagination(page, per_page, total):
    """Same shape as _paginate()'s pagination dict, but for endpoints
    (like /audit) that already page on the backend rather than in
    Python. page/per_page/total come straight from the API response."""
    total_pages = max(1, -(-total // per_page)) if per_page else 1
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    end = start + per_page
    return {
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


@app.route("/")
def index():
    if session.get("token"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        recaptcha_response = request.form.get("g-recaptcha-response", "")
        try:
            resp = requests.post(
                f"{BACKEND_URL}/auth/login",
                data={
                    "username": email,
                    "password": password,
                    "g_recaptcha_response": recaptcha_response,
                },
                timeout=10,
            )
        except requests.RequestException:
            flash("Could not reach the backend. Is it running on BACKEND_URL?", "error")
            return redirect(url_for("login"))

        if resp.status_code == 400:
            detail = resp.json().get("detail", "Please complete the captcha and try again.") if resp.content else "Please complete the captcha and try again."
            flash(detail, "error")
            return redirect(url_for("login"))

        if resp.status_code != 200:
            flash("Incorrect email or password.", "error")
            return redirect(url_for("login"))

        data = resp.json()
        if data.get("mfa_required"):
            session["pre_auth_token"] = data["pre_auth_token"]
            session["pre_auth_email"] = email
            return redirect(url_for("mfa_verify"))
        session["token"] = data["access_token"]
        session["email"] = email
        flash("Logged in successfully.", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html", recaptcha_site_key=RECAPTCHA_SITE_KEY)


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

    return render_template("mfa_verify.html")


@app.route("/mfa/resend", methods=["POST"])
def mfa_resend():
    pre_auth_token = session.get("pre_auth_token")
    if not pre_auth_token:
        return redirect(url_for("login"))
    requests.post(f"{BACKEND_URL}/auth/mfa/resend-otp", json={"pre_auth_token": pre_auth_token}, timeout=10)
    flash("A new code has been sent to your email.", "success")
    return redirect(url_for("mfa_verify"))


@app.route("/security", methods=["GET", "POST"])
def security_settings():
    if not session.get("token"):
        return redirect(url_for("login"))

    if request.method == "POST":
        action = request.form.get("action")
        endpoint = "enable" if action == "enable" else "disable"
        requests.post(f"{BACKEND_URL}/auth/mfa/{endpoint}", headers=_auth_headers(), timeout=10)
        flash(f"Two-factor authentication {'enabled' if endpoint == 'enable' else 'disabled'}.", "success")
        return redirect(url_for("security_settings"))

    me_resp = requests.get(f"{BACKEND_URL}/auth/me", headers=_auth_headers(), timeout=10)
    mfa_enabled = me_resp.json().get("mfa_enabled", False) if me_resp.status_code == 200 else False
    return render_template("security_settings.html", mfa_enabled=mfa_enabled)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        try:
            resp = requests.post(
                f"{BACKEND_URL}/auth/register",
                json={"email": email, "password": password},
                timeout=10,
            )
        except requests.RequestException:
            flash("Could not reach the backend. Is it running on BACKEND_URL?", "error")
            return redirect(url_for("register"))

        if resp.status_code != 201:
            detail = resp.json().get("detail", "Registration failed.") if resp.content else "Registration failed."
            flash(detail, "error")
            return redirect(url_for("register"))

        flash("Account created. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        try:
            requests.post(f"{BACKEND_URL}/auth/forgot-password", json={"email": email}, timeout=10)
        except requests.RequestException:
            pass
        # Always the same message, whether or not the account exists --
        # matches the backend's non-enumerating response.
        flash("If that email is registered, a reset link has been sent.", "success")
        return redirect(url_for("login"))

    return render_template("forgot_password.html")


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    token = request.args.get("token", "") if request.method == "GET" else request.form.get("token", "")

    if request.method == "POST":
        new_password = request.form.get("password", "")
        try:
            resp = requests.post(
                f"{BACKEND_URL}/auth/reset-password",
                json={"token": token, "new_password": new_password},
                timeout=10,
            )
        except requests.RequestException:
            flash("Could not reach the backend. Is it running on BACKEND_URL?", "error")
            return render_template("reset_password.html", token=token)

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
    researcher_id = researcher.get("id")
    role = user.get("role", "researcher")

    def _safe_get(path, params=None):
        """Best-effort GET for dashboard widgets -- a hiccup on any one
        stat (collaborations, review queue, etc.) should never break the
        whole dashboard. Returns None on any non-200 or network error."""
        try:
            r = requests.get(
                f"{BACKEND_URL}{path}", params=params, headers=_auth_headers(), timeout=10
            )
            return r.json() if r.status_code == 200 else None
        except requests.RequestException:
            return None

    publication_count = 0
    conference_count = 0
    recent_publication = None
    collaborator_count = 0
    pending_request_count = 0

    if researcher_id:
        pubs = _safe_get("/publications", {"author_id": researcher_id}) or []
        publication_count = len(pubs)
        recent_publication = pubs[0] if pubs else None

        confs = _safe_get("/conferences", {"researcher_id": researcher_id}) or []
        conference_count = len(confs)

        my_collabs = _safe_get("/collaborations/my", {"page": 1, "page_size": 10})
        if my_collabs:
            collaborator_count = my_collabs.get("total", 0)

        incoming = _safe_get(
            "/collaborations/collaboration-requests",
            {"direction": "incoming", "status": "pending"},
        )
        if incoming:
            pending_request_count = incoming.get("total", 0)

    admin_stats = None
    if role == "system_admin":
        _, admin_stats = _admin_user_stats()

    pending_review_count = 0
    pending_review_preview = []
    if role == "reviewer":
        pending_review = _safe_get("/publications/pending-review") or []
        pending_review_count = len(pending_review)
        pending_review_preview = sorted(pending_review, key=lambda p: p["id"])[:3]

    return render_template(
        "dashboard.html",
        user=user,
        role=role,
        role_label=ROLE_LABEL.get(role, role),
        role_pill_class=ROLE_PILL_CLASS.get(role, "pill-gray"),
        publication_count=publication_count,
        conference_count=conference_count,
        recent_publication=recent_publication,
        collaborator_count=collaborator_count,
        pending_request_count=pending_request_count,
        admin_stats=admin_stats,
        pending_review_count=pending_review_count,
        pending_review_preview=pending_review_preview,
    )


@app.route("/profile")
def profile():
    if not session.get("token"):
        return redirect(url_for("login"))

    resp = requests.get(f"{BACKEND_URL}/researchers/me", headers=_auth_headers(), timeout=10)
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))

    researcher = resp.json() if resp.status_code == 200 else {}
    user = researcher.get("user", {"email": session.get("email"), "role": "researcher"})
    return render_template("profile.html", researcher=researcher, user=user)


@app.route("/profile/edit", methods=["GET", "POST"])
def profile_edit():
    if not session.get("token"):
        return redirect(url_for("login"))

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
            detail = resp.json().get("detail", "Could not save profile.") if resp.content else "Could not save profile."
            flash(detail, "error")
            return redirect(url_for("profile_edit"))
        flash("Profile saved.", "success")
        return redirect(url_for("profile"))

    resp = requests.get(f"{BACKEND_URL}/researchers/me", headers=_auth_headers(), timeout=10)
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))

    researcher = resp.json() if resp.status_code == 200 else {}
    return render_template("profile_edit.html", researcher=researcher)


def _to_int_or_none(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except ValueError:
        return None


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

        institutions = response.json() if response.status_code == 200 else []
    except requests.RequestException:
        institutions = []
        flash("Backend server is not running.", "error")

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

    # System Admin can reassign the institution's admin. The dropdown for
    # that lists all users with the institution_admin role -- fetched via
    # /admin/users, which only exists once the Admin module (Step 8/9) is
    # wired in. Until then this simply stays empty and the dropdown is skipped.
    institution_admins = []
    if _current_role() == "system_admin":
        try:
            users_resp = requests.get(
                f"{BACKEND_URL}/admin/users", headers=_auth_headers(), timeout=10
            )
            if users_resp.status_code == 200:
                institution_admins = [
                    u for u in users_resp.json() if u.get("role") == "institution_admin"
                ]
        except requests.RequestException:
            institution_admins = []

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
            flash("Institution deleted successfully.", "success")
        elif response.status_code == 404:
            flash("Institution not found.", "error")
        elif response.status_code == 401:
            session.clear()
            flash("Session expired. Please login again.", "error")
            return redirect(url_for("login"))
        else:
            flash("Unable to delete institution.", "error")
    except requests.RequestException:
        flash("Backend server is not running.", "error")

    return redirect(url_for("institution"))


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
    role = _current_role()

    params = {}
    if researcher_id:
        params["author_id"] = researcher_id
    if request.args.get("q"):
        params["q"] = request.args["q"]
    if request.args.get("year"):
        params["year"] = request.args["year"]

    pubs = []
    if researcher_id or role == "institution_admin":
        # Institution Admin has no researcher profile (so researcher_id
        # is always None for them) but the backend still scopes the
        # list to their institution on its own -- don't gate the call
        # behind researcher_id or their view would just be empty.
        resp = requests.get(f"{BACKEND_URL}/publications", params=params, headers=_auth_headers(), timeout=10)
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

    resp = requests.get(f"{BACKEND_URL}/publications/{publication_id}", headers=_auth_headers(), timeout=10)
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

    if _current_role() != "reviewer":
        flash("Only a Reviewer can view the review queue.", "error")
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


@app.route("/citations", methods=["GET", "POST"])
def citations():
    if not session.get("token"):
        return redirect(url_for("login"))

    if _current_role() in ("system_admin", "reviewer"):
        flash("Citations are only available to publication authors.", "error")
        return redirect(url_for("dashboard"))

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
            f"{BACKEND_URL}/publications", params={"author_id": researcher_id}, headers=_auth_headers(), timeout=10
        )
        my_publications = my_pubs_resp.json() if my_pubs_resp.status_code == 200 else []

        all_pubs_resp = requests.get(f"{BACKEND_URL}/publications", headers=_auth_headers(), timeout=10)
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

    if _current_role() == "reviewer":
        flash("Citation Insights is not available to Reviewers.", "error")
        return redirect(url_for("dashboard"))

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
        """Returns (json_or_None, status_code, detail). Only a real 401 means
        the session is invalid -- every other non-200 (400 "create a
        profile first", 422 bad params, 500, etc.) is a normal error to
        surface with a flash message, not a reason to log the user out."""
        resp = requests.get(
            f"{BACKEND_URL}{path}", params=params, headers=_auth_headers(), timeout=10
        )
        if resp.status_code == 200:
            return resp.json(), resp.status_code, None
        detail = None
        if resp.content:
            try:
                detail = resp.json().get("detail")
            except ValueError:
                detail = None
        return None, resp.status_code, detail

    incoming, incoming_status, incoming_detail = _get(
        "/collaborations/collaboration-requests",
        {"direction": "incoming", "status": "pending"},
    )
    outgoing, outgoing_status, outgoing_detail = _get(
        "/collaborations/collaboration-requests",
        {"direction": "outgoing", "status": "pending"},
    )
    my_collabs, my_collabs_status, my_collabs_detail = _get(
        "/collaborations/my", {"page": 1, "page_size": 25}
    )

    if 401 in (incoming_status, outgoing_status, my_collabs_status):
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))

    if incoming is None or outgoing is None or my_collabs is None:
        detail = incoming_detail or outgoing_detail or my_collabs_detail
        flash(
            detail or "Could not load your collaborations right now. Please try again.",
            "error",
        )
        return render_template(
            "collaborations.html",
            incoming_requests=[],
            outgoing_requests=[],
            my_collaborations=[],
            directory_results=[],
            q="",
        )

    q = request.args.get("q", "").strip()
    directory_results = []
    if q:
        search_resp = requests.get(
            f"{BACKEND_URL}/researchers/search",
            params={"q": q},
            headers=_auth_headers(),
            timeout=10,
        )
        if search_resp.status_code == 200:
            directory_results = search_resp.json()

    my_researcher_id = None
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
        f"{BACKEND_URL}/collaborations/collaboration-requests",
        json=payload,
        headers=_auth_headers(),
        timeout=10,
    )
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))
    if resp.status_code != 201:
        detail = (
            resp.json().get("detail", "Could not send request.")
            if resp.content
            else "Could not send request."
        )
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
        detail = (
            resp.json().get("detail", "Could not update request.")
            if resp.content
            else "Could not update request."
        )
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

    resp = requests.get(
        f"{BACKEND_URL}/collaborations/{collaboration_id}",
        headers=_auth_headers(),
        timeout=10,
    )
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
        f"{BACKEND_URL}/collaborations/network",
        params={"depth": depth},
        headers=_auth_headers(),
        timeout=10,
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
        f"{BACKEND_URL}/collaborations/suggested",
        params={"limit": 12},
        headers=_auth_headers(),
        timeout=10,
    )
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))

    suggestions = resp.json() if resp.status_code == 200 else []
    return render_template("suggested_collaborators.html", suggestions=suggestions)


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
        return redirect(url_for("conferences"))
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
    return redirect(url_for("conference_detail", conference_id=conference_id))


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


# -----------------------------
# Projects (Module 4: Collaboration Management -- research projects)
# -----------------------------
@app.route("/projects")
def projects():
    if not session.get("token"):
        return redirect(url_for("login"))

    params = {}
    if request.args.get("q"):
        params["q"] = request.args["q"]
    if request.args.get("status_filter"):
        params["status_filter"] = request.args["status_filter"]

    resp = requests.get(f"{BACKEND_URL}/projects", params=params, headers=_auth_headers(), timeout=10)
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))

    project_list = resp.json() if resp.status_code == 200 else []

    sort_by = request.args.get("sort_by", "created_at")
    sort_order = request.args.get("sort_order", "desc")
    allowed_sort_fields = {"created_at", "title", "status"}
    if sort_by not in allowed_sort_fields:
        sort_by = "created_at"
    if sort_order not in {"asc", "desc"}:
        sort_order = "desc"

    project_list = _sort_items(project_list, sort_by, sort_order, allowed_sort_fields, "created_at")
    total_count = len(project_list)
    projects_page, pagination = _paginate(project_list, request)

    return render_template(
        "projects.html",
        projects=projects_page,
        total_count=total_count,
        pagination=pagination,
        sort_by=sort_by,
        status_pill_class=PROJECT_STATUS_PILL_CLASS,
        base_args=_pagination_args(request),
    )


@app.route("/projects/add", methods=["GET", "POST"])
def add_project():
    if not session.get("token"):
        return redirect(url_for("login"))

    inst_resp = requests.get(f"{BACKEND_URL}/institutions/", headers=_auth_headers(), timeout=10)
    institutions = inst_resp.json() if inst_resp.status_code == 200 else []

    if request.method == "POST":
        payload = {
            "title": request.form.get("title", ""),
            "description": request.form.get("description") or None,
            "status": request.form.get("status", "planned"),
            "start_date": request.form.get("start_date") or None,
            "end_date": request.form.get("end_date") or None,
            "institution_id": _to_int_or_none(request.form.get("institution_id")),
        }
        resp = requests.post(
            f"{BACKEND_URL}/projects", json=payload, headers=_auth_headers(), timeout=10
        )
        if resp.status_code == 401:
            session.clear()
            flash("Session expired. Please log in again.", "error")
            return redirect(url_for("login"))
        if resp.status_code != 201:
            detail = resp.json().get("detail", "Could not create project.") if resp.content else "Could not create project."
            flash(detail, "error")
            return redirect(url_for("add_project"))

        flash("Project created.", "success")
        project = resp.json()
        return redirect(url_for("project_detail", project_id=project["id"]))

    return render_template("project_form.html", project=None, institutions=institutions)


@app.route("/projects/<int:project_id>/edit", methods=["GET", "POST"])
def edit_project(project_id):
    if not session.get("token"):
        return redirect(url_for("login"))

    inst_resp = requests.get(f"{BACKEND_URL}/institutions/", headers=_auth_headers(), timeout=10)
    institutions = inst_resp.json() if inst_resp.status_code == 200 else []

    if request.method == "POST":
        payload = {
            "title": request.form.get("title", ""),
            "description": request.form.get("description") or None,
            "status": request.form.get("status", "planned"),
            "start_date": request.form.get("start_date") or None,
            "end_date": request.form.get("end_date") or None,
            "institution_id": _to_int_or_none(request.form.get("institution_id")),
        }
        resp = requests.put(
            f"{BACKEND_URL}/projects/{project_id}", json=payload, headers=_auth_headers(), timeout=10
        )
        if resp.status_code == 401:
            session.clear()
            flash("Session expired. Please log in again.", "error")
            return redirect(url_for("login"))
        if resp.status_code != 200:
            detail = resp.json().get("detail", "Could not update project.") if resp.content else "Could not update project."
            flash(detail, "error")
            return redirect(url_for("edit_project", project_id=project_id))

        flash("Project updated.", "success")
        return redirect(url_for("project_detail", project_id=project_id))

    resp = requests.get(f"{BACKEND_URL}/projects/{project_id}", headers=_auth_headers(), timeout=10)
    if resp.status_code != 200:
        flash("Project not found.", "error")
        return redirect(url_for("projects"))

    return render_template("project_form.html", project=resp.json(), institutions=institutions)


@app.route("/projects/<int:project_id>")
def project_detail(project_id):
    if not session.get("token"):
        return redirect(url_for("login"))

    resp = requests.get(f"{BACKEND_URL}/projects/{project_id}", headers=_auth_headers(), timeout=10)
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))
    if resp.status_code == 403:
        flash("You're not part of this project.", "error")
        return redirect(url_for("projects"))
    if resp.status_code != 200:
        flash("Project not found.", "error")
        return redirect(url_for("projects"))

    project = resp.json()

    researcher = _current_researcher()
    my_researcher_id = researcher.get("id") if researcher else None
    role = _current_role()
    is_lead_or_admin = role == "system_admin" or (
        my_researcher_id is not None and my_researcher_id == project.get("lead_researcher_id")
    )

    # Look up display info (email/department) for each member -- the
    # project payload only carries researcher_id, so enrich it here the
    # same way collaboration/publication pages resolve researcher names.
    members = project.get("members", [])
    for member in members:
        r_resp = requests.get(
            f"{BACKEND_URL}/researchers/{member['researcher_id']}",
            headers=_auth_headers(),
            timeout=10,
        )
        member["researcher"] = r_resp.json() if r_resp.status_code == 200 else None

    institution = None
    if project.get("institution_id"):
        inst_resp = requests.get(
            f"{BACKEND_URL}/institutions/{project['institution_id']}",
            headers=_auth_headers(),
            timeout=10,
        )
        institution = inst_resp.json() if inst_resp.status_code == 200 else None

    return render_template(
        "project_detail.html",
        project=project,
        members=members,
        institution=institution,
        is_lead_or_admin=is_lead_or_admin,
        current_researcher_id=my_researcher_id,
        status_pill_class=PROJECT_STATUS_PILL_CLASS,
    )


@app.route("/projects/<int:project_id>/delete", methods=["POST"])
def delete_project(project_id):
    if not session.get("token"):
        return redirect(url_for("login"))

    resp = requests.delete(
        f"{BACKEND_URL}/projects/{project_id}", headers=_auth_headers(), timeout=10
    )
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))
    if resp.status_code != 204:
        detail = resp.json().get("detail", "Could not delete project.") if resp.content else "Could not delete project."
        flash(detail, "error")
        return redirect(url_for("project_detail", project_id=project_id))

    flash("Project deleted.", "success")
    return redirect(url_for("projects"))


@app.route("/projects/<int:project_id>/members/add", methods=["POST"])
def add_project_member(project_id):
    if not session.get("token"):
        return redirect(url_for("login"))

    payload = {
        "researcher_id": _to_int_or_none(request.form.get("researcher_id")),
        "role_in_project": request.form.get("role_in_project", "member"),
    }
    resp = requests.post(
        f"{BACKEND_URL}/projects/{project_id}/members",
        json=payload,
        headers=_auth_headers(),
        timeout=10,
    )
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))
    if resp.status_code != 200:
        detail = resp.json().get("detail", "Could not send invite.") if resp.content else "Could not send invite."
        flash(detail, "error")
    else:
        flash("Invite sent.", "success")
    return redirect(url_for("project_detail", project_id=project_id))


@app.route("/projects/<int:project_id>/members/respond", methods=["POST"])
def respond_project_invite(project_id):
    if not session.get("token"):
        return redirect(url_for("login"))

    accept = request.form.get("accept") == "1"
    resp = requests.post(
        f"{BACKEND_URL}/projects/{project_id}/members/respond",
        json={"accept": accept},
        headers=_auth_headers(),
        timeout=10,
    )
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))
    if resp.status_code != 200:
        detail = resp.json().get("detail", "Could not respond to invite.") if resp.content else "Could not respond to invite."
        flash(detail, "error")
    else:
        flash("You've joined the project." if accept else "Invite declined.", "success")
    return redirect(url_for("project_detail", project_id=project_id))


@app.route("/projects/<int:project_id>/members/<int:researcher_id>/remove", methods=["POST"])
def remove_project_member(project_id, researcher_id):
    if not session.get("token"):
        return redirect(url_for("login"))

    resp = requests.delete(
        f"{BACKEND_URL}/projects/{project_id}/members/{researcher_id}",
        headers=_auth_headers(),
        timeout=10,
    )
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))
    if resp.status_code != 200:
        detail = resp.json().get("detail", "Could not remove member.") if resp.content else "Could not remove member."
        flash(detail, "error")
    else:
        flash("Member removed.", "success")
    return redirect(url_for("project_detail", project_id=project_id))


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


# -----------------------------
# Reports & Export (Module 8)
# -----------------------------
@app.route("/reports")
def reports():
    if not session.get("token"):
        return redirect(url_for("login"))

    def _get(path):
        resp = requests.get(f"{BACKEND_URL}{path}", headers=_auth_headers(), timeout=10)
        return resp.json() if resp.status_code == 200 else None

    summary = _get("/reports/summary")
    pub_report = _get("/reports/publications")
    project_report = _get("/reports/projects")
    collab_report = _get("/reports/collaborations")

    institution_report = None
    if _current_role() in ("system_admin", "institution_admin"):
        institution_report = _get("/reports/institutions")

    if summary is None:
        resp = requests.get(f"{BACKEND_URL}/reports/summary", headers=_auth_headers(), timeout=10)
        if resp.status_code == 401:
            session.clear()
            flash("Session expired. Please log in again.", "error")
            return redirect(url_for("login"))

    return render_template(
        "reports.html",
        summary=summary,
        pub_report=pub_report,
        project_report=project_report,
        collab_report=collab_report,
        institution_report=institution_report,
    )


@app.route("/reports/export/<report_type>/<fmt>")
def export_report(report_type, fmt):
    if not session.get("token"):
        return redirect(url_for("login"))

    if fmt not in ("excel", "pdf"):
        flash("Unknown export format.", "error")
        return redirect(url_for("reports"))

    resp = requests.get(
        f"{BACKEND_URL}/reports/export/{fmt}",
        params={"type": report_type},
        headers=_auth_headers(),
        timeout=30,
    )
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))
    if resp.status_code != 200:
        flash("Could not generate that export right now.", "error")
        return redirect(url_for("reports"))

    extension = "xlsx" if fmt == "excel" else "pdf"
    content_type = resp.headers.get(
        "Content-Type",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        if fmt == "excel"
        else "application/pdf",
    )
    content_disposition = resp.headers.get(
        "Content-Disposition", f'attachment; filename="{report_type}_report.{extension}"'
    )
    return Response(
        resp.content,
        mimetype=content_type,
        headers={"Content-Disposition": content_disposition},
    )


# -----------------------------
# Audit Log (Module 9) -- System Admin only
# -----------------------------
@app.route("/audit")
def audit_log():
    if not session.get("token"):
        return redirect(url_for("login"))

    if _current_role() != "system_admin":
        flash("Only a System Admin can view the audit log.", "error")
        return redirect(url_for("dashboard"))

    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1
    try:
        page_size = int(request.args.get("page_size", 25))
    except ValueError:
        page_size = 25
    if page_size not in (10, 25, 50, 100):
        page_size = 25

    params = {"page": page, "page_size": page_size}
    if request.args.get("entity_type"):
        params["entity_type"] = request.args["entity_type"]
    if request.args.get("action"):
        params["action"] = request.args["action"]
    if request.args.get("user_id"):
        params["user_id"] = request.args["user_id"]
    if request.args.get("date_from"):
        params["date_from"] = request.args["date_from"]
    if request.args.get("date_to"):
        params["date_to"] = request.args["date_to"]

    resp = requests.get(f"{BACKEND_URL}/audit", params=params, headers=_auth_headers(), timeout=10)
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))
    if resp.status_code == 403:
        flash("Only a System Admin can view the audit log.", "error")
        return redirect(url_for("dashboard"))

    data = resp.json() if resp.status_code == 200 else {"items": [], "total": 0}

    actions_resp = requests.get(f"{BACKEND_URL}/audit/actions", headers=_auth_headers(), timeout=10)
    actions = actions_resp.json() if actions_resp.status_code == 200 else []

    pagination = _server_pagination(page, page_size, data["total"])

    return render_template(
        "audit.html",
        logs=data["items"],
        actions=actions,
        pagination=pagination,
        base_args=_pagination_args(request),
    )


# -----------------------------
# Notifications
# -----------------------------
@app.route("/notifications")
def notifications():
    if not session.get("token"):
        return redirect(url_for("login"))

    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1
    try:
        page_size = int(request.args.get("page_size", 25))
    except ValueError:
        page_size = 25
    if page_size not in (10, 25, 50):
        page_size = 25

    resp = requests.get(
        f"{BACKEND_URL}/notifications",
        params={"page": page, "page_size": page_size},
        headers=_auth_headers(),
        timeout=10,
    )
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))

    data = resp.json() if resp.status_code == 200 else {"items": [], "total": 0, "unread_count": 0}
    pagination = _server_pagination(page, page_size, data["total"])

    return render_template(
        "notifications.html",
        notification_items=data["items"],
        unread_count=data["unread_count"],
        pagination=pagination,
        base_args=_pagination_args(request),
    )


@app.route("/notifications/<int:notification_id>/read", methods=["POST"])
def mark_notification_read(notification_id):
    if not session.get("token"):
        return redirect(url_for("login"))

    resp = requests.patch(
        f"{BACKEND_URL}/notifications/{notification_id}/read",
        headers=_auth_headers(),
        timeout=10,
    )
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))

    link_url = request.form.get("link_url")
    if resp.status_code == 200 and link_url:
        return redirect(link_url)
    return redirect(url_for("notifications"))


@app.route("/notifications/mark-all-read", methods=["POST"])
def mark_all_notifications_read():
    if not session.get("token"):
        return redirect(url_for("login"))

    resp = requests.post(
        f"{BACKEND_URL}/notifications/mark-all-read",
        headers=_auth_headers(),
        timeout=10,
    )
    if resp.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        return redirect(url_for("login"))
    if resp.status_code == 200:
        flash("All notifications marked as read.", "success")
    return redirect(url_for("notifications"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
