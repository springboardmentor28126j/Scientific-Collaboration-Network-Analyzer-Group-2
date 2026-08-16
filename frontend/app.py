from functools import wraps
from collections import Counter
import math

import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash, Response, send_file, abort

import api_client
from api_client import ApiError
from config import FLASK_SECRET_KEY, RECAPTCHA_SITE_KEY
from report_export import build_excel, build_pdf, ReportSection

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

# One entry per portal shown on the "Select User Type" screen.
ROLE_CONFIG = {
    "researcher": {"label": "Researcher", "template": "login_researcher.html"},
    "institution_admin": {"label": "Institution Admin", "template": "login_institution_admin.html"},
    "reviewer": {"label": "Reviewer", "template": "login_reviewer.html"},
    "system_admin": {"label": "System Admin", "template": "login_system_admin.html"},
}

# ---------------------------------------------------------------------------
# Dashboard chart helpers
#
# The four dashboards each show a handful of "X by status" breakdowns
# (publications, conferences, projects, reviews, user roles). Rather than
# reach for a JS charting library, these build plain SVG donut/bar geometry
# server-side so the dashboards stay dependency-free -- the same spirit as
# the hand-rolled network graph and report bar charts already in this app.
#
# Colors deliberately mirror the existing .badge-<status> palette (see
# style.css) so a "published" badge and a "published" donut slice always
# mean the same color throughout the app.
# ---------------------------------------------------------------------------
STATUS_CHART_COLORS = {
    "published": "#0EA66B", "accepted": "#0EA66B", "completed": "#0EA66B", "accept": "#0EA66B",
    "submitted": "#E0A73E", "under_review": "#E0A73E", "pending": "#E0A73E", "minor_revision": "#E0A73E",
    "draft": "#9B9790", "rejected": "#9B9790", "archived": "#9B9790", "planned": "#9B9790",
    "registration_open": "#5B4FE8", "ongoing": "#5B4FE8", "assigned": "#5B4FE8",
    "cancelled": "#DC6B5E", "declined": "#DC6B5E", "major_revision": "#DC6B5E", "reject": "#DC6B5E",
}
ROLE_CHART_COLORS = {
    "researcher": "#5B4FE8", "institution_admin": "#E0A73E",
    "reviewer": "#0EA66B", "system_admin": "#4E8FB0",
}
DEFAULT_CHART_COLOR = "#9B9790"


def donut_chart_data(counts, color_map=None, size=112, stroke=14):
    """Turn a {label: count} dict into ready-to-render SVG donut geometry:
    one stacked <circle> per segment, positioned with stroke-dasharray /
    stroke-dashoffset so they read clockwise from 12 o'clock. See the
    dash_donut macro in _dash_widgets.html for the rendering side."""
    color_map = color_map or STATUS_CHART_COLORS
    counts = {k: v for k, v in (counts or {}).items() if v}
    total = sum(counts.values())
    radius = (size - stroke) / 2
    circumference = 2 * math.pi * radius
    segments = []
    cursor = 0.0
    for label, count in counts.items():
        pct = (count / total) if total else 0
        length = pct * circumference
        segments.append({
            "label": label,
            "display_label": label.replace("_", " ").capitalize(),
            "count": count,
            "pct": round(pct * 100),
            "color": color_map.get(label, DEFAULT_CHART_COLOR),
            "dash": f"{length:.3f} {circumference:.3f}",
            "offset": f"{-cursor:.3f}",
        })
        cursor += length
    return {
        "segments": segments, "total": total, "size": size, "stroke": stroke,
        "radius": radius, "circumference": circumference, "center": size / 2,
    }


def bar_chart_data(counts, color_map=None):
    """Turn a {label: count} dict into a simple ranked bar list: each item
    gets a color (mirroring the badge palette) and a 0-100 percent-of-max
    width for its bar."""
    color_map = color_map or STATUS_CHART_COLORS
    counts = {k: v for k, v in (counts or {}).items() if v}
    peak = max(counts.values()) if counts else 0
    items = []
    for label, count in sorted(counts.items(), key=lambda kv: kv[1], reverse=True):
        items.append({
            "label": label,
            "display_label": label.replace("_", " ").capitalize(),
            "count": count,
            "pct": round((count / peak) * 100) if peak else 0,
            "color": color_map.get(label, DEFAULT_CHART_COLOR),
        })
    return items


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "access_token" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapped


def role_required(*allowed_roles):
    """Like login_required, but also requires session['user_role'] to be one
    of allowed_roles. Used to hide/guard System Admin-only pages such as
    /admin/* -- the backend enforces the same restriction independently, this
    just gives a friendlier redirect instead of a raw 403 from the API."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if "access_token" not in session:
                flash("Please log in to continue.", "warning")
                return redirect(url_for("login"))
            if session.get("user_role") not in allowed_roles:
                flash("You do not have permission to view that page.", "danger")
                return redirect(url_for("dashboard"))
            return view_func(*args, **kwargs)
        return wrapped
    return decorator


@app.context_processor
def inject_unread_message_count():
    """Same pattern as inject_unread_notification_count, for the
    'My Collaborators' sidebar badge -- unread private messages across
    every collaboration, not just one thread."""
    if "access_token" not in session:
        return {"unread_message_count": 0}
    try:
        return {"unread_message_count": api_client.get_unread_message_count(session["access_token"])}
    except Exception:
        return {"unread_message_count": 0}


def _store_user_session(access_token, refresh_token):
    session["access_token"] = access_token
    session["refresh_token"] = refresh_token
    try:
        account = api_client.get_my_account(access_token)
        session["user_email"] = account["email"]
        session["user_role"] = account["role"]
        session["user_institution_id"] = account.get("institution_id")
        local_part = account["email"].split("@")[0]
        parts = [p for p in local_part.replace(".", " ").replace("_", " ").split(" ") if p]
        session["user_initials"] = "".join(p[0].upper() for p in parts[:2]) if parts else "??"
        session["user_username"] = parts[0].capitalize() if parts else local_part
    except ApiError:
        session["user_email"] = ""
        session["user_role"] = ""
        session["user_institution_id"] = None
        session["user_initials"] = "??"
        session["user_username"] = ""

@app.route("/")
def index():
    if "access_token" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


def _webmail_link(email: str) -> tuple[str | None, str | None]:
    domain = email.split("@")[-1].lower()
    providers = {
        "gmail.com": ("https://mail.google.com/mail/u/?authuser=" + email, "Open Gmail"),
        "outlook.com": ("https://outlook.live.com/mail/0/inbox", "Open Outlook"),
        "hotmail.com": ("https://outlook.live.com/mail/0/inbox", "Open Outlook"),
        "yahoo.com": ("https://mail.yahoo.com", "Open Yahoo Mail"),
    }
    return providers.get(domain, (None, None))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]
        institution_id_raw = request.form.get("institution_id")
        institution_id = int(institution_id_raw) if institution_id_raw else None
        institution_name = request.form.get("institution_name") or None
        website = request.form.get("website") or None
        domain = request.form.get("domain") or None
        address = request.form.get("address") or None
        official_email = request.form.get("official_email") or None
        try:
            api_client.register(
                email,
                password,
                role,
                institution_id,
                institution_name=institution_name,
                website=website,
                domain=domain,
                address=address,
                official_email=official_email,
            )
            webmail_url, webmail_label = _webmail_link(email)
            return render_template(
                "check_email.html", email=email, webmail_url=webmail_url, webmail_label=webmail_label
            )
        except ApiError as e:
            flash(f"Registration failed: {e.detail}", "danger")

    try:
        institutions = api_client.list_institutions()
    except ApiError:
        institutions = []
    preselect_role = request.args.get("role") if request.method == "GET" else None
    return render_template("register.html", institutions=institutions, preselect_role=preselect_role)


@app.route("/check-email", methods=["POST"])
def check_email():
    email = (request.get_json(silent=True) or {}).get("email", "")
    try:
        result = api_client.check_email_deliverability(email)
        return result
    except ApiError:
        # Fail open -- never let this block registration.
        return {"checked": False, "is_valid": None, "reason": None}


@app.route("/verify-email")
def verify_email():
    token = request.args.get("token")
    if not token:
        flash("Missing verification token.", "danger")
        return redirect(url_for("login"))
    try:
        result = api_client.verify_email(token)
        flash(result.get("message", "Email verified successfully."), "success")
    except ApiError as e:
        flash(f"Verification failed: {e.detail}", "danger")
    return redirect(url_for("login"))


@app.route("/resend-verification", methods=["POST"])
def resend_verification():
    email = request.form.get("email", "")
    try:
        result = api_client.resend_verification(email)
        flash(result.get("message", "If needed, a new link was sent."), "info")
    except ApiError as e:
        flash(f"Could not resend: {e.detail}", "danger")
    return redirect(url_for("login"))


@app.route("/login")
def login():
    """The 'Select User Type' screen -- picks which of the four login pages to use."""
    return render_template("login_select.html")


def _captcha_session_key(role):
    return f"captcha_required_{role}"


@app.route("/login/<role>", methods=["GET", "POST"])
def login_role(role):
    cfg = ROLE_CONFIG.get(role)
    if cfg is None:
        flash("Unknown user type.", "danger")
        return redirect(url_for("login"))

    captcha_required = session.get(_captcha_session_key(role), False)

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        recaptcha_token = request.form.get("g-recaptcha-response")
        try:
            tokens = api_client.login(email, password, recaptcha_token=recaptcha_token)
            session.pop(_captcha_session_key(role), None)
            _store_user_session(tokens["access_token"], tokens["refresh_token"])
            mismatch = _redirect_for_role_mismatch(role)
            if mismatch:
                return mismatch
            flash("Logged in successfully.", "success")
            return redirect(url_for("dashboard"))
        except ApiError as e:
            # The backend replies with a structured {"error": ...} detail
            # once too many failed attempts have piled up for this email,
            # so the CAPTCHA step can be told apart from a plain wrong
            # password and kept showing across attempts.
            error_code = e.detail.get("error") if isinstance(e.detail, dict) else None
            if error_code in ("captcha_required", "captcha_invalid"):
                session[_captcha_session_key(role)] = True
                captcha_required = True
                message = e.detail.get("message", "Please verify you're not a robot to continue.")
                flash(message, "danger")
            else:
                detail = e.detail.get("message", str(e.detail)) if isinstance(e.detail, dict) else e.detail
                flash(f"Login failed: {detail}", "danger")

    return render_template(
        cfg["template"],
        captcha_required=captcha_required,
        recaptcha_site_key=RECAPTCHA_SITE_KEY if captcha_required else None,
    )

def _redirect_for_role_mismatch(expected_role):
    """After a successful login, make sure the account actually belongs to the
    portal the person logged in from -- e.g. a Researcher account used on the
    System Admin page. Returns a redirect response if there's a mismatch, else None."""
    actual_role = session.get("user_role")
    if actual_role == expected_role:
        return None
    session.clear()
    actual_cfg = ROLE_CONFIG.get(actual_role)
    actual_label = actual_cfg["label"] if actual_cfg else (actual_role or "a different user type")
    flash(f"This account is registered as {actual_label}. Please log in from the {actual_label} portal.", "danger")
    if actual_cfg:
        return redirect(url_for("login_role", role=actual_role))
    return redirect(url_for("login"))

@app.route("/auth/google-session", methods=["POST"])
def google_session():
    data = request.get_json(silent=True) or {}
    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token")
    expected_role = data.get("expected_role")
    if not access_token or not refresh_token:
        return {"error": "Missing tokens"}, 400
    _store_user_session(access_token, refresh_token)
    if expected_role and session.get("user_role") != expected_role:
        actual_role = session.get("user_role")
        session.clear()
        return {"error": "role_mismatch", "actual_role": actual_role}, 403
    return {"ok": True}


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    """Landing page after login. Every role used to see the same generic
    page here -- now this just figures out the account's role and routes
    it to that role's own dashboard, so each user type gets a view built
    around what they actually do (an admin sees platform stats, a reviewer
    sees their review queue, etc.) instead of one shared page."""
    access_token = session["access_token"]
    try:
        account = api_client.get_my_account(access_token)
    except ApiError as e:
        if e.status_code == 401:
            session.clear()
            flash("Your session expired. Please log in again.", "warning")
            return redirect(url_for("login"))
        flash(f"Could not load account: {e.detail}", "danger")
        return render_template("researcher_dashboard.html", account=None, profile=None, institution=None, publication_count=None)

    if account["role"] == "system_admin":
        return redirect(url_for("admin_dashboard"))
    if account["role"] == "institution_admin":
        return redirect(url_for("institution_admin_dashboard"))
    if account["role"] == "reviewer":
        return redirect(url_for("reviewer_dashboard"))

    # Researcher is the default/fallback dashboard.
    profile = None
    institution = None
    institution_options = []
    publication_count = None
    pub_status_chart = None
    recent_publications = []
    leaderboard = None
    if account["role"] == "researcher":
        profile = api_client.get_my_researcher_profile(access_token)
        # The dashboard's "Institution" card is about the researcher's own
        # affiliation (set at signup, often via email-domain matching), not
        # their department -- that's a separate, optional assignment made
        # later and frequently left blank. Fall back to the department's
        # institution only if the account itself has none on file.
        if account.get("institution_id"):
            try:
                institution = api_client.get_institution(access_token, account["institution_id"])
            except ApiError:
                institution = None
        else:
            # No institution on file yet -- give them a way to set it
            # themselves instead of just showing "Not set" with no path
            # forward (e.g. their institution's email domain wasn't
            # configured when they signed up, so auto-detection had
            # nothing to match against).
            try:
                institution_options = api_client.list_institutions(access_token)
            except ApiError:
                institution_options = []
        try:
            pubs = api_client.list_publications(access_token, page=1, page_size=50, mine=True)
            items = pubs.get("items", [])
            publication_count = pubs.get("total", 0)
            status_counts = Counter(p["status"] for p in items)
            pub_status_chart = donut_chart_data(status_counts)
            recent_publications = sorted(items, key=lambda p: p.get("updated_at") or "", reverse=True)[:5]
        except ApiError:
            publication_count = None
        try:
            leaderboard = api_client.get_citation_analytics(access_token, limit=5)
        except ApiError:
            leaderboard = None

    return render_template(
        "researcher_dashboard.html", account=account, profile=profile, institution=institution,
        institution_options=institution_options,
        publication_count=publication_count, pub_status_chart=pub_status_chart,
        recent_publications=recent_publications, leaderboard=leaderboard,
    )

@app.route("/profile/institution", methods=["POST"])
@login_required
def set_my_institution_route():
    access_token = session["access_token"]
    institution_id = request.form.get("institution_id", type=int)
    if not institution_id:
        flash("Please choose an institution.", "danger")
        return redirect(url_for("dashboard"))
    try:
        api_client.set_my_institution(access_token, institution_id)
        flash(
            "Institution linked. If it needs your institution admin's approval, "
            "you'll be notified once it's reviewed.",
            "success",
        )
    except ApiError as e:
        flash(f"Could not set institution: {e.detail}", "danger")
    return redirect(url_for("dashboard"))


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    access_token = session["access_token"]

    if request.method == "POST":
        data = {
            "first_name": request.form["first_name"],
            "last_name": request.form["last_name"],
            "academic_title": request.form.get("academic_title") or None,
            "orcid_id": request.form.get("orcid_id") or None,
            "bio": request.form.get("bio") or None,
        }
        existing = api_client.get_my_researcher_profile(access_token)
        try:
            if existing is None:
                api_client.create_researcher_profile(access_token, data)
                flash("Researcher profile created.", "success")
            else:
                api_client.update_researcher_profile(access_token, data)
                flash("Researcher profile updated.", "success")
        except ApiError as e:
            flash(f"Could not save profile: {e.detail}", "danger")
        return redirect(url_for("profile"))

    profile_data = api_client.get_my_researcher_profile(access_token)
    return render_template("profile.html", profile=profile_data)


@app.route("/profile/skills", methods=["POST"])
@login_required
def add_skill():
    access_token = session["access_token"]
    name = request.form.get("skill_name", "").strip()
    if name:
        try:
            api_client.add_skill(access_token, name)
            flash(f"Added skill '{name}'.", "success")
        except ApiError as e:
            flash(f"Could not add skill: {e.detail}", "danger")
    return redirect(url_for("profile"))


@app.route("/profile/skills/<int:skill_id>/remove", methods=["POST"])
@login_required
def remove_skill(skill_id):
    access_token = session["access_token"]
    try:
        api_client.remove_skill(access_token, skill_id)
        flash("Skill removed.", "info")
    except ApiError as e:
        flash(f"Could not remove skill: {e.detail}", "danger")
    return redirect(url_for("profile"))


@app.route("/profile/interests", methods=["POST"])
@login_required
def add_interest():
    access_token = session["access_token"]
    name = request.form.get("interest_name", "").strip()
    if name:
        try:
            api_client.add_interest(access_token, name)
            flash(f"Added interest '{name}'.", "success")
        except ApiError as e:
            flash(f"Could not add interest: {e.detail}", "danger")
    return redirect(url_for("profile"))


@app.route("/profile/interests/<int:interest_id>/remove", methods=["POST"])
@login_required
def remove_interest(interest_id):
    access_token = session["access_token"]
    try:
        api_client.remove_interest(access_token, interest_id)
        flash("Interest removed.", "info")
    except ApiError as e:
        flash(f"Could not remove interest: {e.detail}", "danger")
    return redirect(url_for("profile"))


@app.route("/institutions")
@login_required
def institutions():
    access_token = session["access_token"]
    try:
        results = api_client.list_institutions(access_token)
    except ApiError as e:
        flash(f"Could not load institutions: {e.detail}", "danger")
        results = []
    return render_template("institutions.html", institutions=results)


@app.route("/institutions/new", methods=["GET", "POST"])
@login_required
def new_institution():
    access_token = session["access_token"]
    if request.method == "POST":
        data = {
            "name": request.form["name"],
            "type": request.form.get("type") or None,
            "country": request.form.get("country") or None,
            "address": request.form.get("address") or None,
            "email_domain": request.form.get("email_domain") or None,
        }
        try:
            api_client.create_institution(access_token, data)
            flash("Institution created.", "success")
            return redirect(url_for("institutions"))
        except ApiError as e:
            flash(f"Could not create institution: {e.detail}", "danger")
    return render_template("institution_form.html", institution=None)


@app.route("/institutions/<int:institution_id>")
@login_required
def institution_detail(institution_id):
    access_token = session["access_token"]
    try:
        institution = api_client.get_institution(access_token, institution_id)
        departments = api_client.list_departments(access_token, institution_id)
    except ApiError as e:
        flash(f"Could not load institution: {e.detail}", "danger")
        return redirect(url_for("institutions"))
    return render_template("institution_detail.html", institution=institution, departments=departments)


@app.route("/institutions/<int:institution_id>/edit", methods=["GET", "POST"])
@login_required
def edit_institution(institution_id):
    access_token = session["access_token"]
    if request.method == "POST":
        data = {
            "name": request.form["name"],
            "type": request.form.get("type") or None,
            "country": request.form.get("country") or None,
            "address": request.form.get("address") or None,
            "email_domain": request.form.get("email_domain") or None,
        }
        try:
            api_client.update_institution(access_token, institution_id, data)
            flash("Institution updated.", "success")
            return redirect(url_for("institution_detail", institution_id=institution_id))
        except ApiError as e:
            flash(f"Could not update institution: {e.detail}", "danger")

    try:
        institution = api_client.get_institution(access_token, institution_id)
    except ApiError as e:
        flash(f"Could not load institution: {e.detail}", "danger")
        return redirect(url_for("institutions"))
    return render_template("institution_form.html", institution=institution)


@app.route("/institutions/<int:institution_id>/delete", methods=["POST"])
@login_required
def delete_institution(institution_id):
    access_token = session["access_token"]
    try:
        api_client.delete_institution(access_token, institution_id)
        flash("Institution deleted.", "info")
    except ApiError as e:
        flash(f"Could not delete institution: {e.detail}", "danger")
    return redirect(url_for("institutions"))


@app.route("/institutions/<int:institution_id>/departments", methods=["POST"])
@login_required
def add_department(institution_id):
    access_token = session["access_token"]
    data = {"name": request.form["name"], "code": request.form.get("code") or None}
    try:
        api_client.create_department(access_token, institution_id, data)
        flash("Department added.", "success")
    except ApiError as e:
        flash(f"Could not add department: {e.detail}", "danger")
    return redirect(url_for("institution_detail", institution_id=institution_id))


@app.route("/institutions/<int:institution_id>/departments/<int:department_id>/delete", methods=["POST"])
@login_required
def remove_department(institution_id, department_id):
    access_token = session["access_token"]
    try:
        api_client.delete_department(access_token, institution_id, department_id)
        flash("Department removed.", "info")
    except ApiError as e:
        flash(f"Could not remove department: {e.detail}", "danger")
    return redirect(url_for("institution_detail", institution_id=institution_id))


@app.route("/publications")
@login_required
def publications():
    access_token = session["access_token"]
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 10, type=int)
    institution_id = request.args.get("institution_id", type=int)
    author_id = request.args.get("author_id", type=int)
    year = request.args.get("year", type=int)
    q = request.args.get("q") or None
    sort_by = request.args.get("sort_by", "date")
    sort_dir = request.args.get("sort_dir", "desc")
    mine = request.args.get("mine") == "true"
    if page_size not in (10, 25, 50):
        page_size = 10
    if sort_by not in ("date", "title"):
        sort_by = "date"
    if sort_dir not in ("asc", "desc"):
        sort_dir = "desc"
    try:
        result = api_client.list_publications(
            access_token, page=page, page_size=page_size, institution_id=institution_id, mine=mine,
            author_id=author_id, year=year, q=q, sort_by=sort_by, sort_dir=sort_dir,
        )
    except ApiError as e:
        flash(f"Could not load publications: {e.detail}", "danger")
        result = {"items": [], "total": 0, "page": page, "page_size": page_size}
    return render_template(
        "publications.html", result=result, page=page, page_size=page_size, mine=mine,
        author_id=author_id, year=year, q=q or "", sort_by=sort_by, sort_dir=sort_dir,
    )


@app.route("/publications/new", methods=["GET", "POST"])
@login_required
def new_publication():
    access_token = session["access_token"]
    if request.method == "POST":
        data = {
            "title": request.form["title"],
            "abstract": request.form.get("abstract") or None,
            "publication_type": request.form["publication_type"],
            "venue_name": request.form.get("venue_name") or None,
            "doi": request.form.get("doi") or None,
            "publication_date": request.form.get("publication_date") or None,
            "co_author_ids": [int(rid) for rid in request.form.getlist("co_author_ids")],
        }
        try:
            api_client.create_publication(access_token, data)
            flash("Publication created.", "success")
            return redirect(url_for("publications"))
        except ApiError as e:
            flash(f"Could not create publication: {e.detail}", "danger")

    try:
        researchers = api_client.search_researchers(access_token)
    except ApiError:
        researchers = []
    return render_template("publication_form.html", publication=None, researchers=researchers)


@app.route("/publications/<int:publication_id>/edit", methods=["GET", "POST"])
@login_required
def edit_publication(publication_id):
    access_token = session["access_token"]
    if request.method == "POST":
        data = {
            "title": request.form["title"],
            "abstract": request.form.get("abstract") or None,
            "venue_name": request.form.get("venue_name") or None,
            "doi": request.form.get("doi") or None,
            "publication_date": request.form.get("publication_date") or None,
            "status": request.form["status"],
            "co_author_ids": [int(rid) for rid in request.form.getlist("co_author_ids")],
        }
        try:
            api_client.update_publication(access_token, publication_id, data)
            flash("Publication updated.", "success")
            return redirect(url_for("publication_detail", publication_id=publication_id))
        except ApiError as e:
            flash(f"Could not update publication: {e.detail}", "danger")

    try:
        publication = api_client.get_publication(access_token, publication_id)
        researchers = api_client.search_researchers(access_token)
    except ApiError as e:
        flash(f"Could not load publication: {e.detail}", "danger")
        return redirect(url_for("publications"))
    return render_template("publication_form.html", publication=publication, researchers=researchers)


# --- Changes to make in frontend/app.py ---

# 1. FIND your existing publication_detail route and REPLACE it with this
#    (adds fetching the account so the template can check account.role):

@app.route("/publications/<int:publication_id>")
@login_required
def publication_detail(publication_id):
    access_token = session["access_token"]
    try:
        publication = api_client.get_publication(access_token, publication_id)
        account = api_client.get_my_account(access_token)
    except ApiError as e:
        flash(f"Could not load publication: {e.detail}", "danger")
        return redirect(url_for("publications"))

    is_owner = False
    try:
        my_profile = api_client.get_my_researcher_profile(access_token)
        is_owner = bool(my_profile) and my_profile["researcher_id"] == publication["primary_author_id"]
    except ApiError:
        pass

    reviewers = []
    if account["role"] in ("system_admin", "institution_admin"):
        try:
            reviewers = api_client.list_all_users(access_token, role="reviewer", page_size=100)
        except ApiError:
            reviewers = []

    try:
        reviews = api_client.list_reviews_for_target(access_token, "publication", publication_id)
    except ApiError:
        reviews = []

    try:
        references = api_client.list_publication_references(access_token, publication_id)["items"]
    except ApiError:
        references = []
    try:
        cited_by = api_client.list_publication_cited_by(access_token, publication_id)["items"]
    except ApiError:
        cited_by = []
    try:
        citation_text = api_client.get_citation_text(access_token, publication_id)
    except ApiError:
        citation_text = None

    return render_template(
        "publication_detail.html", publication=publication, account=account, reviewers=reviewers,
        reviews=reviews, is_owner=is_owner,
        references=references, cited_by=cited_by, citation_text=citation_text,
    )


@app.route("/publications/<int:publication_id>/assign-reviewer", methods=["POST"])
@role_required("system_admin", "institution_admin")
def assign_publication_reviewer(publication_id):
    access_token = session["access_token"]
    reviewer_id = request.form.get("reviewer_id", type=int)
    try:
        api_client.assign_review(access_token, "publication", publication_id, reviewer_id)
        flash("Reviewer assigned.", "success")
    except ApiError as e:
        flash(f"Could not assign reviewer: {e.detail}", "danger")
    return redirect(url_for("publication_detail", publication_id=publication_id))


# 2. ADD this new route -- anywhere near the other publication routes:

@app.route("/publications/<int:publication_id>/set-status", methods=["POST"])
@login_required
def set_publication_status(publication_id):
    access_token = session["access_token"]
    new_status = request.form["status"]
    try:
        api_client.update_publication_status(access_token, publication_id, new_status)
        flash("Publication status updated.", "success")
    except ApiError as e:
        flash(f"Could not update status: {e.detail}", "danger")
    return redirect(url_for("publication_detail", publication_id=publication_id))


@app.route("/publications/<int:publication_id>/upload", methods=["POST"])
@login_required
def upload_publication(publication_id):
    access_token = session["access_token"]
    file = request.files.get("file")
    if not file or not file.filename:
        flash("Please choose a file to upload.", "danger")
        return redirect(url_for("publication_detail", publication_id=publication_id))
    try:
        api_client.upload_publication_file(access_token, publication_id, file)
        flash("File uploaded.", "success")
    except ApiError as e:
        flash(f"Could not upload file: {e.detail}", "danger")
    return redirect(url_for("publication_detail", publication_id=publication_id))

@app.route("/reports/citations")
@login_required
def citation_reports():
    access_token = session["access_token"]
    limit = request.args.get("limit", default=10, type=int)
    try:
        data = api_client.get_citation_analytics(access_token, limit=limit)
    except ApiError as e:
        flash(f"Could not load citation reports: {e.detail}", "danger")
        data = {"top_papers": [], "influential_papers": [], "top_researchers": [], "top_institutions": []}
    return render_template("citation_reports.html", data=data, limit=limit)

# --- Citation management ---

@app.route("/publications/<int:publication_id>/citations", methods=["POST"])
@login_required
def add_citation_route(publication_id):
    access_token = session["access_token"]
    internal_id = request.form.get("cited_publication_id", type=int)

    if internal_id:
        data = {"cited_publication_id": internal_id, "context": request.form.get("context") or None}
    else:
        title = (request.form.get("external_title") or "").strip()
        if not title:
            flash("Enter either an existing publication ID or an external title.", "danger")
            return redirect(url_for("publication_detail", publication_id=publication_id))
        data = {
            "external_title": title,
            "external_authors": request.form.get("external_authors") or None,
            "external_venue": request.form.get("external_venue") or None,
            "external_year": request.form.get("external_year", type=int),
            "external_doi": request.form.get("external_doi") or None,
            "context": request.form.get("context") or None,
        }

    try:
        api_client.add_citation(access_token, publication_id, data)
        flash("Citation added.", "success")
    except ApiError as e:
        flash(f"Could not add citation: {e.detail}", "danger")
    return redirect(url_for("publication_detail", publication_id=publication_id))


@app.route("/citations/<int:citation_id>/delete", methods=["POST"])
@login_required
def delete_citation_route(citation_id):
    access_token = session["access_token"]
    publication_id = request.form.get("publication_id", type=int)
    try:
        api_client.delete_citation(access_token, citation_id)
        flash("Citation removed.", "info")
    except ApiError as e:
        flash(f"Could not remove citation: {e.detail}", "danger")
    return redirect(url_for("publication_detail", publication_id=publication_id) if publication_id else url_for("publications"))


@app.route("/publications/<int:publication_id>/download")
@login_required
def download_publication(publication_id):
    access_token = session["access_token"]
    resp = requests.get(
        f"{BACKEND_API_URL}/publications/{publication_id}/download",
        headers=api_client._auth_header(access_token),
        stream=True,
    )
    if resp.status_code != 200:
        flash("Could not download file.", "danger")
        return redirect(url_for("publication_detail", publication_id=publication_id))

    content_disposition = resp.headers.get("content-disposition", "attachment")
    return Response(
        resp.iter_content(chunk_size=8192),
        content_type=resp.headers.get("content-type", "application/octet-stream"),
        headers={"Content-Disposition": content_disposition},
    )


@app.route("/publications/<int:publication_id>/delete", methods=["POST"])
@login_required
def delete_publication(publication_id):
    access_token = session["access_token"]
    try:
        api_client.delete_publication(access_token, publication_id)
        flash("Publication deleted.", "info")
    except ApiError as e:
        flash(f"Could not delete publication: {e.detail}", "danger")
    return redirect(url_for("publications"))


@app.route("/conferences")
@login_required
def conferences():
    access_token = session["access_token"]
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 10, type=int)
    mine = request.args.get("mine") == "true"
    ours = request.args.get("ours") == "true"
    author_id = request.args.get("author_id", type=int)
    year = request.args.get("year", type=int)
    q = request.args.get("q") or None
    sort_by = request.args.get("sort_by", "date")
    sort_dir = request.args.get("sort_dir", "desc")
    if page_size not in (10, 25, 50):
        page_size = 10
    if sort_by not in ("date", "name"):
        sort_by = "date"
    if sort_dir not in ("asc", "desc"):
        sort_dir = "desc"
    institution_id = session.get("user_institution_id") if (ours and session.get("user_role") == "institution_admin") else None
    try:
        result = api_client.list_conferences(
            access_token, page=page, page_size=page_size, mine=mine, institution_id=institution_id,
            author_id=author_id, year=year, q=q, sort_by=sort_by, sort_dir=sort_dir,
        )
    except ApiError as e:
        flash(f"Could not load conferences: {e.detail}", "danger")
        result = {"items": [], "total": 0, "page": page, "page_size": page_size}
    return render_template(
        "conferences.html", result=result, page=page, page_size=page_size, mine=mine, ours=ours,
        author_id=author_id, year=year, q=q or "", sort_by=sort_by, sort_dir=sort_dir,
    )


@app.route("/conferences/new", methods=["GET", "POST"])
@role_required("system_admin", "institution_admin")
def new_conference():
    access_token = session["access_token"]
    if request.method == "POST":
        data = {
            "name": request.form["name"],
            "description": request.form.get("description") or None,
            "start_date": request.form["start_date"],
            "end_date": request.form["end_date"],
            "location": request.form.get("location") or None,
            "website_url": request.form.get("website_url") or None,
        }
        try:
            api_client.create_conference(access_token, data)
            flash("Conference created.", "success")
            return redirect(url_for("conferences"))
        except ApiError as e:
            flash(f"Could not create conference: {e.detail}", "danger")
    return render_template("conference_form.html", conference=None)


@app.route("/conferences/<int:conference_id>/edit", methods=["GET", "POST"])
@role_required("system_admin", "institution_admin")
def edit_conference(conference_id):
    access_token = session["access_token"]
    if request.method == "POST":
        data = {
            "name": request.form["name"],
            "description": request.form.get("description") or None,
            "start_date": request.form["start_date"],
            "end_date": request.form["end_date"],
            "location": request.form.get("location") or None,
            "website_url": request.form.get("website_url") or None,
            "status": request.form["status"],
        }
        try:
            api_client.update_conference(access_token, conference_id, data)
            flash("Conference updated.", "success")
            return redirect(url_for("conference_detail", conference_id=conference_id))
        except ApiError as e:
            flash(f"Could not update conference: {e.detail}", "danger")

    try:
        conference = api_client.get_conference(access_token, conference_id)
    except ApiError as e:
        flash(f"Could not load conference: {e.detail}", "danger")
        return redirect(url_for("conferences"))
    return render_template("conference_form.html", conference=conference)


@app.route("/conferences/<int:conference_id>")
@login_required
def conference_detail(conference_id):
    access_token = session["access_token"]
    try:
        conference = api_client.get_conference(access_token, conference_id)
        participants = api_client.list_conference_participants(access_token, conference_id)
        my_profile = api_client.get_my_researcher_profile(access_token)
        account = api_client.get_my_account(access_token)
    except ApiError as e:
        flash(f"Could not load conference: {e.detail}", "danger")
        return redirect(url_for("conferences"))
    my_researcher_id = my_profile["researcher_id"] if my_profile else None

    is_manager = account["role"] == "system_admin" or (
        account["role"] == "institution_admin" and conference.get("organizing_institution_id") == account.get("institution_id")
    )

    reviewers = []
    if is_manager:
        try:
            reviewers = api_client.list_all_users(access_token, role="reviewer", page_size=100)
        except ApiError:
            reviewers = []

    reviews_by_participation = {}
    if is_manager:
        for p in participants:
            try:
                reviews_by_participation[p["participation_id"]] = api_client.list_reviews_for_target(
                    access_token, "conference_submission", p["participation_id"]
                )
            except ApiError:
                reviews_by_participation[p["participation_id"]] = []

    return render_template(
        "conference_detail.html", conference=conference, participants=participants,
        my_researcher_id=my_researcher_id, reviewers=reviewers, is_manager=is_manager,
        reviews_by_participation=reviews_by_participation,
    )


@app.route("/conferences/<int:conference_id>/delete", methods=["POST"])
@role_required("system_admin", "institution_admin")
def delete_conference(conference_id):
    access_token = session["access_token"]
    try:
        api_client.delete_conference(access_token, conference_id)
        flash("Conference deleted.", "info")
    except ApiError as e:
        flash(f"Could not delete conference: {e.detail}", "danger")
        return redirect(url_for("conference_detail", conference_id=conference_id))
    return redirect(url_for("conferences"))


@app.route("/conferences/<int:conference_id>/participants/<int:participation_id>/assign-reviewer", methods=["POST"])
@role_required("system_admin", "institution_admin")
def assign_conference_reviewer(conference_id, participation_id):
    access_token = session["access_token"]
    reviewer_id = request.form.get("reviewer_id", type=int)
    try:
        api_client.assign_review(access_token, "conference_submission", participation_id, reviewer_id)
        flash("Reviewer assigned.", "success")
    except ApiError as e:
        flash(f"Could not assign reviewer: {e.detail}", "danger")
    return redirect(url_for("conference_detail", conference_id=conference_id))


@app.route("/conferences/<int:conference_id>/participants/<int:participation_id>/status", methods=["POST"])
@role_required("system_admin", "institution_admin")
def set_participation_status(conference_id, participation_id):
    access_token = session["access_token"]
    new_status = request.form["submission_status"]
    try:
        api_client.update_conference_participation(
            access_token, conference_id, participation_id, {"submission_status": new_status}
        )
        flash("Submission status updated.", "success")
    except ApiError as e:
        flash(f"Could not update status: {e.detail}", "danger")
    return redirect(url_for("conference_detail", conference_id=conference_id))


@app.route("/conferences/<int:conference_id>/participants/<int:participation_id>/certificate")
@login_required
def download_certificate(conference_id, participation_id):
    access_token = session["access_token"]
    resp = requests.get(
        f"{BACKEND_API_URL}/conferences/{conference_id}/participants/{participation_id}/certificate",
        headers=api_client._auth_header(access_token),
        stream=True,
    )
    if resp.status_code != 200:
        try:
            flash(f"Could not download certificate: {resp.json().get('detail', 'unknown error')}", "danger")
        except ValueError:
            flash("Could not download certificate.", "danger")
        return redirect(url_for("conference_detail", conference_id=conference_id))

    content_disposition = resp.headers.get("content-disposition", "attachment")
    return Response(
        resp.iter_content(chunk_size=8192),
        content_type=resp.headers.get("content-type", "application/octet-stream"),
        headers={"Content-Disposition": content_disposition},
    )


@app.route("/conferences/<int:conference_id>/participants/<int:participation_id>/submit", methods=["POST"])
@login_required
def submit_participation(conference_id, participation_id):
    access_token = session["access_token"]
    try:
        api_client.update_conference_participation(
            access_token, conference_id, participation_id, {"submission_status": "submitted"}
        )
        flash("Submitted for review.", "success")
    except ApiError as e:
        flash(f"Could not submit: {e.detail}", "danger")
    return redirect(url_for("conference_detail", conference_id=conference_id))


@app.route("/conferences/<int:conference_id>/participants/<int:participation_id>/cancel", methods=["POST"])
@login_required
def cancel_participation(conference_id, participation_id):
    access_token = session["access_token"]
    try:
        api_client.cancel_conference_participation(access_token, conference_id, participation_id)
        flash("Registration cancelled.", "info")
    except ApiError as e:
        flash(f"Could not cancel registration: {e.detail}", "danger")
    return redirect(url_for("conference_detail", conference_id=conference_id))


@app.route("/conferences/<int:conference_id>/participants/<int:participation_id>/update", methods=["POST"])
@login_required
def update_participation(conference_id, participation_id):
    access_token = session["access_token"]
    data = {
        "role": request.form["role"],
        "presentation_title": request.form.get("presentation_title") or None,
    }
    try:
        api_client.update_conference_participation(access_token, conference_id, participation_id, data)
        flash("Registration updated.", "success")
    except ApiError as e:
        flash(f"Could not update registration: {e.detail}", "danger")
    return redirect(url_for("conference_detail", conference_id=conference_id))


@app.route("/conferences/<int:conference_id>/register", methods=["POST"])
@login_required
def register_conference(conference_id):
    access_token = session["access_token"]
    publication_id = request.form.get("publication_id", type=int)
    data = {
        "role": request.form["role"],
        "presentation_title": request.form.get("presentation_title") or None,
        "publication_id": publication_id,
    }
    try:
        api_client.register_for_conference(access_token, conference_id, data)
        flash("Registered for conference.", "success")
    except ApiError as e:
        flash(f"Could not register: {e.detail}", "danger")
    return redirect(url_for("conference_detail", conference_id=conference_id))


@app.route("/researchers")
@login_required
def researcher_directory():
    access_token = session["access_token"]
    skill = request.args.get("skill") or None
    interest = request.args.get("interest") or None
    try:
        results = api_client.search_researchers(access_token, skill=skill, interest=interest)
    except ApiError as e:
        flash(f"Search failed: {e.detail}", "danger")
        results = []

    my_researcher_id = None
    collaborator_ids = set()
    outgoing_pending_ids = set()
    incoming_pending_ids = set()
    try:
        my_profile = api_client.get_my_researcher_profile(access_token)
        my_researcher_id = my_profile["researcher_id"] if my_profile else None
    except ApiError:
        pass
    if my_researcher_id:
        try:
            my_collabs = api_client.list_my_collaborations(access_token, page=1, page_size=50)
            collaborator_ids = {c["partner"]["researcher_id"] for c in my_collabs["items"] if c.get("partner")}
        except ApiError:
            pass
        try:
            outgoing = api_client.list_collaboration_requests(access_token, direction="outgoing", status_filter="pending")
            outgoing_pending_ids = {r["addressee"]["researcher_id"] for r in outgoing["items"]}
            incoming = api_client.list_collaboration_requests(access_token, direction="incoming", status_filter="pending")
            incoming_pending_ids = {r["requester"]["researcher_id"]: r["collaboration_request_id"] for r in incoming["items"]}
        except ApiError:
            incoming_pending_ids = {}

    return render_template(
        "directory.html", results=results, skill=skill or "", interest=interest or "",
        my_researcher_id=my_researcher_id, collaborator_ids=collaborator_ids,
        outgoing_pending_ids=outgoing_pending_ids, incoming_pending_ids=incoming_pending_ids,
    )


@app.route("/collaborations/connect/<int:researcher_id>", methods=["POST"])
@login_required
def send_collaboration_request_route(researcher_id):
    access_token = session["access_token"]
    message = request.form.get("message") or None
    try:
        api_client.send_collaboration_request(access_token, researcher_id, message=message)
        flash("Connection request sent.", "success")
    except ApiError as e:
        flash(f"Could not send request: {e.detail}", "danger")
    return redirect(request.referrer or url_for("researcher_directory"))


@app.route("/collaborations")
@login_required
def my_collaborations():
    access_token = session["access_token"]
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 10, type=int)
    if page_size not in (10, 25, 50):
        page_size = 10
    try:
        result = api_client.list_my_collaborations(access_token, page=page, page_size=page_size)
    except ApiError as e:
        flash(f"Could not load your collaborators: {e.detail}", "danger")
        result = {"items": [], "total": 0, "page": page, "page_size": page_size}
    return render_template("collaborations.html", result=result, page=page, page_size=page_size)


@app.route("/collaborations/network")
@login_required
def collaboration_network():
    access_token = session["access_token"]
    depth = request.args.get("depth", 2, type=int)
    if depth not in (1, 2, 3):
        depth = 2
    try:
        graph = api_client.get_collaboration_network(access_token, depth=depth)
    except ApiError as e:
        flash(f"Could not load your network: {e.detail}", "danger")
        graph = {"nodes": [], "edges": []}

    width, height, radius = 640, 440, 170
    center_x, center_y = width / 2, height / 2
    positions = {}
    center_node = next((n for n in graph["nodes"] if n["is_center"]), None)
    others = [n for n in graph["nodes"] if not n["is_center"]]
    if center_node:
        positions[center_node["researcher_id"]] = (center_x, center_y)
    count = max(len(others), 1)
    for i, node in enumerate(others):
        angle = (2 * math.pi * i) / count
        positions[node["researcher_id"]] = (
            center_x + radius * math.cos(angle),
            center_y + radius * math.sin(angle),
        )
    for node in graph["nodes"]:
        x, y = positions.get(node["researcher_id"], (center_x, center_y))
        node["x"], node["y"] = round(x, 1), round(y, 1)

    return render_template(
        "collaboration_network.html", graph=graph, depth=depth, svg_width=width, svg_height=height,
        positions=positions,
    )


@app.route("/collaborations/suggested")
@login_required
def suggested_collaborators():
    access_token = session["access_token"]
    try:
        suggestions = api_client.list_suggested_collaborators(access_token, limit=15)
    except ApiError as e:
        flash(f"Could not load suggestions: {e.detail}", "danger")
        suggestions = []
    return render_template("suggested_collaborators.html", suggestions=suggestions)


@app.route("/collaborations/timeline")
@login_required
def collaboration_timeline():
    access_token = session["access_token"]
    try:
        result = api_client.list_my_collaborations(access_token, page=1, page_size=50)
        events = sorted(
            result["items"],
            key=lambda c: c.get("first_collaboration") or c["created_at"],
        )
    except ApiError as e:
        flash(f"Could not load your collaboration timeline: {e.detail}", "danger")
        events = []
    return render_template("collaboration_timeline.html", events=events)


@app.route("/collaborations/requests")
@login_required
def collaboration_requests():
    access_token = session["access_token"]
    box = request.args.get("box", "incoming")
    if box not in ("incoming", "outgoing"):
        box = "incoming"
    try:
        result = api_client.list_collaboration_requests(access_token, direction=box)
    except ApiError as e:
        flash(f"Could not load requests: {e.detail}", "danger")
        result = {"items": [], "total": 0}
    return render_template("collaboration_requests.html", result=result, box=box)


@app.route("/collaborations/requests/<int:collaboration_request_id>/respond", methods=["POST"])
@login_required
def respond_collaboration_request_route(collaboration_request_id):
    access_token = session["access_token"]
    new_status = request.form["status"]
    notification_id = request.form.get("notification_id", type=int)
    try:
        api_client.respond_to_collaboration_request(access_token, collaboration_request_id, new_status)
        if notification_id:
            try:
                api_client.mark_notification_read(access_token, notification_id)
            except ApiError:
                pass
        flash(
            "Connection request accepted." if new_status == "accepted" else "Connection request declined.",
            "success" if new_status == "accepted" else "info",
        )
    except ApiError as e:
        flash(f"Could not update request: {e.detail}", "danger")
    return redirect(url_for("notifications"))

@app.route("/collaborations/<int:collaboration_id>")
@login_required
def collaboration_detail(collaboration_id):
    access_token = session["access_token"]
    try:
        collaboration = api_client.get_collaboration(access_token, collaboration_id)
    except ApiError as e:
        flash(f"Could not load collaboration: {e.detail}", "danger")
        return redirect(url_for("my_collaborations"))

    try:
        my_profile = api_client.get_my_researcher_profile(access_token)
        my_researcher_id = my_profile["researcher_id"] if my_profile else None
    except ApiError:
        my_researcher_id = None

    try:
        messages = api_client.list_messages(access_token, collaboration_id)["items"]
    except ApiError as e:
        flash(f"Could not load messages: {e.detail}", "danger")
        messages = []

    return render_template(
        "collaboration_detail.html", collaboration=collaboration, messages=messages, my_researcher_id=my_researcher_id,
    )


@app.route("/collaborations/<int:collaboration_id>/messages", methods=["POST"])
@login_required
def send_message_route(collaboration_id):
    access_token = session["access_token"]
    body = request.form.get("body", "")
    try:
        api_client.send_message(access_token, collaboration_id, body)
    except ApiError as e:
        flash(f"Could not send message: {e.detail}", "danger")
    return redirect(url_for("collaboration_detail", collaboration_id=collaboration_id) + "#message-thread-end")


@app.route("/admin")
@role_required("system_admin")
def admin_dashboard():
    access_token = session["access_token"]
    try:
        stats = api_client.get_dashboard_stats(access_token)
    except ApiError as e:
        flash(f"Could not load dashboard stats: {e.detail}", "danger")
        stats = None

    charts = {}
    leaderboard = None
    if stats:
        charts["roles"] = donut_chart_data(stats.get("users_by_role"), color_map=ROLE_CHART_COLORS)
        charts["publications"] = donut_chart_data(stats.get("publications_by_status"))
        charts["conferences"] = donut_chart_data(stats.get("conferences_by_status"))
        charts["projects"] = donut_chart_data(stats.get("projects_by_status"))
        try:
            leaderboard = api_client.get_citation_analytics(access_token, limit=5)
        except ApiError:
            leaderboard = None

    return render_template("admin_dashboard.html", stats=stats, charts=charts, leaderboard=leaderboard)


@app.route("/admin/users")
@role_required("system_admin")
def admin_users():
    access_token = session["access_token"]
    role_filter = request.args.get("role") or None
    affiliation_filter = request.args.get("affiliation_status") or None
    try:
        users = api_client.list_all_users(
            access_token, role=role_filter, affiliation_status=affiliation_filter, page_size=100,
        )
    except ApiError as e:
        flash(f"Could not load users: {e.detail}", "danger")
        users = []
    return render_template(
        "admin_users.html", users=users, role_filter=role_filter or "", affiliation_filter=affiliation_filter or "",
    )


@app.route("/admin/users/<int:user_id>/approve-affiliation", methods=["POST"])
@role_required("system_admin")
def admin_approve_affiliation(user_id):
    access_token = session["access_token"]
    try:
        # Same endpoint institution admins use for their own researchers --
        # System Admin approval is what activates a pending Institution
        # Admin application (institution_id set or a new institution request).
        api_client.approve_affiliation(access_token, user_id)
        flash("Affiliation approved and account activated.", "success")
    except ApiError as e:
        flash(f"Could not approve affiliation: {e.detail}", "danger")
    return redirect(url_for("admin_users"))


@app.route("/admin/users/<int:user_id>/reject-affiliation", methods=["POST"])
@role_required("system_admin")
def admin_reject_affiliation(user_id):
    access_token = session["access_token"]
    try:
        api_client.reject_affiliation(access_token, user_id)
        flash("Affiliation rejected.", "info")
    except ApiError as e:
        flash(f"Could not reject affiliation: {e.detail}", "danger")
    return redirect(url_for("admin_users"))


@app.route("/admin/users/<int:user_id>/update", methods=["POST"])
@role_required("system_admin")
def admin_update_user(user_id):
    access_token = session["access_token"]
    data = {}
    new_role = request.form.get("role")
    if new_role:
        data["role"] = new_role
    is_active = request.form.get("is_active")
    if is_active is not None:
        data["is_active"] = is_active == "true"
    try:
        api_client.admin_update_user(access_token, user_id, data)
        flash("User updated.", "success")
    except ApiError as e:
        flash(f"Could not update user: {e.detail}", "danger")
    return redirect(url_for("admin_users"))


@app.route("/admin/users/<int:user_id>/deactivate", methods=["POST"])
@role_required("system_admin")
def admin_deactivate_user(user_id):
    access_token = session["access_token"]
    try:
        api_client.deactivate_user(access_token, user_id)
        flash("User deactivated.", "info")
    except ApiError as e:
        flash(f"Could not deactivate user: {e.detail}", "danger")
    return redirect(url_for("admin_users"))


@app.route("/admin/audit-logs")
@role_required("system_admin")
def admin_audit_logs():
    access_token = session["access_token"]
    page = request.args.get("page", 1, type=int)
    entity_type = request.args.get("entity_type") or None
    action = request.args.get("action") or None
    try:
        result = api_client.list_audit_logs(access_token, page=page, entity_type=entity_type, action=action)
    except ApiError as e:
        flash(f"Could not load audit logs: {e.detail}", "danger")
        result = {"items": [], "total": 0, "page": page, "page_size": 25}
    return render_template(
        "admin_audit_logs.html", result=result, page=page, entity_type=entity_type or "", action=action or ""
    )


@app.route("/admin/institution-requests")
@role_required("system_admin")
def admin_institution_requests():
    access_token = session["access_token"]
    try:
        requests_data = api_client.list_institution_requests(access_token)
    except ApiError as e:
        flash(f"Could not load institution requests: {e.detail}", "danger")
        requests_data = []
    return render_template("admin_institution_requests.html", requests=requests_data)


@app.route("/admin/institution-requests/<int:request_id>/approve", methods=["POST"])
@role_required("system_admin")
def admin_approve_institution_request(request_id):
    access_token = session["access_token"]
    try:
        api_client.approve_institution_request(access_token, request_id)
        flash("Institution request approved.", "success")
    except ApiError as e:
        flash(f"Could not approve request: {e.detail}", "danger")
    return redirect(url_for("admin_institution_requests"))


@app.route("/admin/institution-requests/<int:request_id>/reject", methods=["POST"])
@role_required("system_admin")
def admin_reject_institution_request(request_id):
    access_token = session["access_token"]
    try:
        api_client.reject_institution_request(access_token, request_id)
        flash("Institution request rejected.", "info")
    except ApiError as e:
        flash(f"Could not reject request: {e.detail}", "danger")
    return redirect(url_for("admin_institution_requests"))


@app.route("/admin/settings", methods=["GET", "POST"])
@role_required("system_admin")
def admin_settings():
    access_token = session["access_token"]
    if request.method == "POST":
        key = request.form.get("key", "").strip()
        value = request.form.get("value", "")
        description = request.form.get("description") or None
        if key:
            try:
                api_client.update_setting(access_token, key, value, description)
                flash(f"Setting '{key}' saved.", "success")
            except ApiError as e:
                flash(f"Could not save setting: {e.detail}", "danger")
        return redirect(url_for("admin_settings"))

    try:
        settings_list = api_client.list_settings(access_token)
    except ApiError as e:
        flash(f"Could not load settings: {e.detail}", "danger")
        settings_list = []
    return render_template("admin_settings.html", settings=settings_list)


@app.route("/institution-admin")
@role_required("institution_admin")
def institution_admin_dashboard():
    access_token = session["access_token"]
    institution_id = session.get("user_institution_id")
    stats = None
    institution = None
    charts = {}
    if institution_id:
        try:
            stats = api_client.get_institution_stats(access_token, institution_id)
            institution = api_client.get_institution(access_token, institution_id)
        except ApiError as e:
            flash(f"Could not load institution reports: {e.detail}", "danger")
    else:
        flash("Your account isn't linked to an institution yet.", "warning")

    if stats:
        charts["publications"] = donut_chart_data(stats.get("publications_by_status"))
        charts["conferences"] = donut_chart_data(stats.get("conferences_by_status"))
        charts["projects"] = donut_chart_data(stats.get("projects_by_status"))

    return render_template("institution_admin_dashboard.html", stats=stats, institution=institution, charts=charts)

 
def _send_report(report_title: str, summary: list, sections: list, fmt: str, filename_base: str):
    """Turns a report's already-computed data into a downloadable file.
    fmt must be 'xlsx' or 'pdf' -- routes validate this before calling."""
    if fmt == "xlsx":
        buf = build_excel(report_title, summary, sections)
        return send_file(
            buf, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True, download_name=f"{filename_base}.xlsx",
        )
    buf = build_pdf(report_title, summary, sections)
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name=f"{filename_base}.pdf")


ALLOWED_REPORTS = {
    # Which report types each role can reach. system_admin is deliberately
    # the union of every key here (oversight access to all report types),
    # rather than being special-cased at each call site.
    "researcher": {"researcher", "publications", "projects", "conferences", "collaborations"},
    "reviewer": {"researcher", "reviews"},
    "institution_admin": {"institution", "publications", "projects", "conferences"},
    "system_admin": {
        "researcher", "publications", "projects", "conferences",
        "collaborations", "reviews", "institution", "system",
    },
}


def _report_allowed(role, report_key):
    return report_key in ALLOWED_REPORTS.get(role, set())


def _guard_report(role, report_key):
    """Returns a redirect response if this role can't reach this report,
    else None. Callers do: `if (resp := _guard_report(role, 'x')): return resp`."""
    if _report_allowed(role, report_key):
        return None
    flash("You don't have access to that report.", "warning")
    return redirect(url_for("reports"))


@app.route("/reports")
@login_required
def reports():
    """Reports index — lists all report types the current user can access."""
    role = session.get("user_role", "")
    return render_template("reports/index.html", role=role, allowed_reports=ALLOWED_REPORTS.get(role, set()))


def _counts_to_dict(labeled_counts):
    """Backend reports return [{"label": ..., "count": ...}, ...] --
    templates were written against plain {label: count} dicts (built by
    the old Python-side aggregation loops), so this is the one adapter
    point that keeps every template unchanged."""
    return {d["label"]: d["count"] for d in labeled_counts}


@app.route("/reports/researcher")
@login_required
def report_researcher():
    access_token = session["access_token"]
    role = session.get("user_role", "")
    if (resp := _guard_report(role, "researcher")):
        return resp
    profile, report = None, None
    try:
        profile = api_client.get_my_researcher_profile(access_token)
    except ApiError:
        # No researcher profile is an expected state for admin accounts --
        # they aren't researchers themselves. Only the report call below
        # needs to actually complain about anything else going wrong.
        profile = None
    try:
        report = api_client.get_researcher_report(access_token)
    except ApiError as e:
        if e.status_code not in (400, 404):
            flash(f"Could not load researcher report: {e.detail}", "danger")
        report = None

    publications = report["publications"] if report else []
    projects = report["projects"] if report else []
    collaborations = report["collaborations"] if report else []
    reviews = report["reviews"] if report else []
    pub_by_status = _counts_to_dict(report["publications_by_status"]) if report else {}
    pub_by_type = _counts_to_dict(report["publications_by_type"]) if report else {}

    return render_template(
        "reports/researcher.html",
        profile=profile, publications=publications, projects=projects,
        collaborations=collaborations, reviews=reviews,
        pub_by_status=pub_by_status, pub_by_type=pub_by_type, role=role,
        has_profile=report is not None,
    )


@app.route("/reports/researcher/export/<fmt>")
@login_required
def report_researcher_export(fmt):
    if fmt not in ("xlsx", "pdf"):
        abort(404)
    access_token = session["access_token"]
    role = session.get("user_role", "")
    if (resp := _guard_report(role, "researcher")):
        return resp
    try:
        profile = api_client.get_my_researcher_profile(access_token)
    except ApiError:
        profile = None
    try:
        report = api_client.get_researcher_report(access_token)
    except ApiError as e:
        flash(f"Could not load researcher report: {e.detail}", "danger")
        return redirect(url_for("report_researcher"))

    name = f"{profile['first_name']} {profile['last_name']}" if profile else "Researcher"
    summary = [
        ("Researcher", name),
        ("Publications", report["publication_count"]),
        ("Projects", report["project_count"]),
        ("Collaborators", report["collaboration_count"]),
    ]
    if role == "reviewer":
        summary.append(("Reviews assigned", report["review_count"]))

    sections = [
        ReportSection("Publications", ["Title", "Type", "Status", "Year", "Venue"], [
            [p["title"], p["publication_type"], p["status"], p["year"], p["venue_name"]] for p in report["publications"]
        ]),
        ReportSection("Projects", ["Title", "Status", "Start date", "End date"], [
            [p["title"], p["status"], p["start_date"], p["end_date"]] for p in report["projects"]
        ]),
        ReportSection("Collaborators", ["Name", "Strength", "First collaboration", "Last collaboration"], [
            [c["name"], c["strength"], c["first_collaboration"], c["last_collaboration"]] for c in report["collaborations"]
        ]),
    ]
    if role == "reviewer":
        sections.append(ReportSection("Reviews", ["Target type", "Status", "Recommendation"], [
            [r["target_type"], r["status"], r["recommendation"] or "pending"] for r in report["reviews"]
        ]))

    return _send_report("Researcher Report", summary, sections, fmt, "researcher_report")


@app.route("/reports/institution")
@login_required
def report_institution():
    access_token = session["access_token"]
    role = session.get("user_role", "")
    if (resp := _guard_report(role, "institution")):
        return resp

    institutions = []
    if role == "system_admin":
        # A system_admin isn't affiliated with any institution, so there's
        # no session-stored institution to fall back on -- let them pick
        # which one to view instead of hitting a dead end.
        try:
            institutions = api_client.list_institutions(access_token)
        except ApiError:
            institutions = []
        institution_id = request.args.get("institution_id", type=int)
        if institution_id is None and institutions:
            institution_id = institutions[0]["institution_id"]
    else:
        institution_id = session.get("user_institution_id")

    stats, institution, researchers, publications, projects, conferences = None, None, [], [], [], []
    if institution_id:
        try:
            institution = api_client.get_institution(access_token, institution_id)
            report = api_client.get_institution_report(access_token, institution_id)
            stats = {
                "total_researchers": report["total_researchers"],
                "approved_researchers": report["approved_researchers"],
                "pending_affiliation_requests": report["pending_researchers"],
                "total_departments": report["total_departments"],
                "total_publications": report["total_publications"],
                "total_projects": report["total_projects"],
                "total_conferences": report["total_conferences"],
            }
            researchers = report["researchers"]
            publications = report["publications"]
            projects = report["projects"]
            conferences = report["conferences"]
        except ApiError as e:
            flash(f"Could not load institution report: {e.detail}", "danger")
    elif role != "system_admin":
        flash("Your account is not linked to an institution. Contact a system admin to assign your institution.", "warning")
    return render_template(
        "reports/institution.html",
        stats=stats, institution=institution, researchers=researchers,
        publications=publications, projects=projects, conferences=conferences, role=role,
        institutions=institutions, selected_institution_id=institution_id,
    )


@app.route("/reports/institution/export/<fmt>")
@login_required
def report_institution_export(fmt):
    if fmt not in ("xlsx", "pdf"):
        abort(404)
    access_token = session["access_token"]
    role = session.get("user_role", "")
    if (resp := _guard_report(role, "institution")):
        return resp
    if role == "system_admin":
        institution_id = request.args.get("institution_id", type=int)
    else:
        institution_id = session.get("user_institution_id")
    if not institution_id:
        flash("Your account is not linked to an institution.", "warning")
        return redirect(url_for("report_institution"))
    try:
        institution = api_client.get_institution(access_token, institution_id)
        report = api_client.get_institution_report(access_token, institution_id)
    except ApiError as e:
        flash(f"Could not load institution report: {e.detail}", "danger")
        return redirect(url_for("report_institution"))

    summary = [
        ("Institution", institution.get("name") if institution else "—"),
        ("Total researchers", report["total_researchers"]),
        ("Approved researchers", report["approved_researchers"]),
        ("Pending researchers", report["pending_researchers"]),
        ("Departments", report["total_departments"]),
        ("Publications", report["total_publications"]),
        ("Conferences", report["total_conferences"]),
    ]
    sections = [
        ReportSection("Researchers", ["Name", "Email", "Active", "Approved"], [
            [r["name"], r["email"], r["is_active"], r["is_approved"]] for r in report["researchers"]
        ]),
        ReportSection("Publications", ["Title", "Type", "Status", "Year"], [
            [p["title"], p["publication_type"], p["status"], p["year"]] for p in report["publications"]
        ]),
        ReportSection("Projects", ["Title", "Status", "Start date", "End date"], [
            [p["title"], p["status"], p["start_date"], p["end_date"]] for p in report["projects"]
        ]),
        ReportSection("Conferences", ["Name", "Status", "Start date", "Location"], [
            [c["name"], c["status"], c["start_date"], c["location"]] for c in report["conferences"]
        ]),
    ]
    return _send_report("Institution Report", summary, sections, fmt, "institution_report")


@app.route("/reports/publications")
@login_required
def report_publications():
    access_token = session["access_token"]
    role = session.get("user_role", "")
    if (resp := _guard_report(role, "publications")):
        return resp
    mine = request.args.get("mine") == "true"
    year_filter = request.args.get("year", type=int)
    try:
        report = api_client.get_publications_report(access_token, mine=mine, year=year_filter)
    except ApiError as e:
        flash(f"Could not load publications report: {e.detail}", "danger")
        report = {"items": [], "by_status": [], "by_type": []}
    return render_template(
        "reports/publications.html",
        publications=report["items"], by_status=_counts_to_dict(report["by_status"]),
        by_type=_counts_to_dict(report["by_type"]), mine=mine, year_filter=year_filter, role=role,
    )


@app.route("/reports/publications/export/<fmt>")
@login_required
def report_publications_export(fmt):
    if fmt not in ("xlsx", "pdf"):
        abort(404)
    access_token = session["access_token"]
    role = session.get("user_role", "")
    if (resp := _guard_report(role, "publications")):
        return resp
    mine = request.args.get("mine") == "true"
    year_filter = request.args.get("year", type=int)
    try:
        report = api_client.get_publications_report(access_token, mine=mine, year=year_filter)
    except ApiError as e:
        flash(f"Could not load publications report: {e.detail}", "danger")
        return redirect(url_for("report_publications"))

    summary = [("Total publications", report["total"])]
    summary += [(f"Status: {d['label']}", d["count"]) for d in sorted(report["by_status"], key=lambda d: d["label"])]
    summary += [(f"Type: {d['label']}", d["count"]) for d in sorted(report["by_type"], key=lambda d: d["label"])]

    sections = [
        ReportSection("Publications", ["Title", "Type", "Status", "Year", "Venue"], [
            [p["title"], p["publication_type"], p["status"], p["year"], p["venue_name"]] for p in report["items"]
        ]),
    ]
    return _send_report("Publications Report", summary, sections, fmt, "publications_report")


@app.route("/reports/projects")
@login_required
def report_projects():
    access_token = session["access_token"]
    role = session.get("user_role", "")
    if (resp := _guard_report(role, "projects")):
        return resp
    mine = request.args.get("mine") == "true"
    try:
        report = api_client.get_projects_report(access_token, mine=mine)
    except ApiError as e:
        flash(f"Could not load projects report: {e.detail}", "danger")
        report = {"items": [], "by_status": []}
    return render_template(
        "reports/projects.html",
        projects=report["items"], by_status=_counts_to_dict(report["by_status"]), mine=mine, role=role,
    )


@app.route("/reports/projects/export/<fmt>")
@login_required
def report_projects_export(fmt):
    if fmt not in ("xlsx", "pdf"):
        abort(404)
    access_token = session["access_token"]
    role = session.get("user_role", "")
    if (resp := _guard_report(role, "projects")):
        return resp
    mine = request.args.get("mine") == "true"
    try:
        report = api_client.get_projects_report(access_token, mine=mine)
    except ApiError as e:
        flash(f"Could not load projects report: {e.detail}", "danger")
        return redirect(url_for("report_projects"))

    summary = [("Total projects", report["total"])]
    summary += [(f"Status: {d['label']}", d["count"]) for d in sorted(report["by_status"], key=lambda d: d["label"])]
    sections = [
        ReportSection("Projects", ["Title", "Status", "Start date", "End date"], [
            [p["title"], p["status"], p["start_date"], p["end_date"]] for p in report["items"]
        ]),
    ]
    return _send_report("Projects Report", summary, sections, fmt, "projects_report")


@app.route("/reports/conferences")
@login_required
def report_conferences():
    access_token = session["access_token"]
    role = session.get("user_role", "")
    if (resp := _guard_report(role, "conferences")):
        return resp
    mine = request.args.get("mine") == "true"
    try:
        report = api_client.get_conferences_report(access_token, mine=mine)
    except ApiError as e:
        flash(f"Could not load conferences report: {e.detail}", "danger")
        report = {"items": [], "by_status": []}
    return render_template(
        "reports/conferences.html",
        conferences=report["items"], by_status=_counts_to_dict(report["by_status"]), mine=mine, role=role,
    )


@app.route("/reports/conferences/export/<fmt>")
@login_required
def report_conferences_export(fmt):
    if fmt not in ("xlsx", "pdf"):
        abort(404)
    access_token = session["access_token"]
    role = session.get("user_role", "")
    if (resp := _guard_report(role, "conferences")):
        return resp
    mine = request.args.get("mine") == "true"
    try:
        report = api_client.get_conferences_report(access_token, mine=mine)
    except ApiError as e:
        flash(f"Could not load conferences report: {e.detail}", "danger")
        return redirect(url_for("report_conferences"))

    summary = [("Total conferences", report["total"])]
    summary += [(f"Status: {d['label']}", d["count"]) for d in sorted(report["by_status"], key=lambda d: d["label"])]
    sections = [
        ReportSection("Conferences", ["Name", "Status", "Start date", "End date", "Location"], [
            [c["name"], c["status"], c["start_date"], c["end_date"], c["location"]] for c in report["items"]
        ]),
    ]
    return _send_report("Conferences Report", summary, sections, fmt, "conferences_report")


@app.route("/reports/reviews")
@login_required
def report_reviews():
    access_token = session["access_token"]
    role = session.get("user_role", "")
    if (resp := _guard_report(role, "reviews")):
        return resp
    try:
        report = api_client.get_reviews_report(access_token)
    except ApiError as e:
        flash(f"Could not load reviews report: {e.detail}", "danger")
        report = {"items": [], "by_status": [], "by_recommendation": [], "completed": 0, "total": 0, "scope": "mine"}

    by_type = {}
    for r in report["items"]:
        t = r.get("target_type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1

    return render_template(
        "reports/reviews.html",
        reviews=report["items"], by_status=_counts_to_dict(report["by_status"]), by_type=by_type,
        by_recommendation=_counts_to_dict(report["by_recommendation"]), completed=report["completed"], role=role,
        scope=report.get("scope", "mine"),
    )


@app.route("/reports/reviews/export/<fmt>")
@login_required
def report_reviews_export(fmt):
    if fmt not in ("xlsx", "pdf"):
        abort(404)
    access_token = session["access_token"]
    role = session.get("user_role", "")
    if (resp := _guard_report(role, "reviews")):
        return resp
    try:
        report = api_client.get_reviews_report(access_token)
    except ApiError as e:
        flash(f"Could not load reviews report: {e.detail}", "danger")
        return redirect(url_for("report_reviews"))

    scope = report.get("scope", "mine")
    summary = [("Total reviews", report["total"]), ("Completed", report["completed"])]
    summary += [(f"Status: {d['label']}", d["count"]) for d in sorted(report["by_status"], key=lambda d: d["label"])]
    summary += [(f"Recommendation: {d['label']}", d["count"]) for d in sorted(report["by_recommendation"], key=lambda d: d["label"])]

    if scope == "all":
        sections = [
            ReportSection("Reviews", ["Reviewer", "Target type", "Status", "Recommendation", "Assigned at"], [
                [r.get("reviewer_name") or "—", r["target_type"], r["status"], r["recommendation"] or "pending", r["assigned_at"]]
                for r in report["items"]
            ]),
        ]
        title = "Reviews Report (System-wide)"
    else:
        sections = [
            ReportSection("Reviews", ["Target type", "Status", "Recommendation", "Assigned at"], [
                [r["target_type"], r["status"], r["recommendation"] or "pending", r["assigned_at"]] for r in report["items"]
            ]),
        ]
        title = "Reviews Report"
    return _send_report(title, summary, sections, fmt, "reviews_report")


@app.route("/reports/collaborations")
@login_required
def report_collaborations():
    access_token = session["access_token"]
    role = session.get("user_role", "")
    if (resp := _guard_report(role, "collaborations")):
        return resp
    try:
        report = api_client.get_collaborations_report(access_token)
    except ApiError as e:
        if e.status_code not in (400, 404):
            flash(f"Could not load collaborations report: {e.detail}", "danger")
        report = {"items": [], "total_strength": 0}
    return render_template(
        "reports/collaborations.html",
        collaborations=report["items"], total_strength=report["total_strength"], role=role,
    )


@app.route("/reports/collaborations/export/<fmt>")
@login_required
def report_collaborations_export(fmt):
    if fmt not in ("xlsx", "pdf"):
        abort(404)
    access_token = session["access_token"]
    role = session.get("user_role", "")
    if (resp := _guard_report(role, "collaborations")):
        return resp
    try:
        report = api_client.get_collaborations_report(access_token)
    except ApiError as e:
        flash(f"Could not load collaborations report: {e.detail}", "danger")
        return redirect(url_for("report_collaborations"))

    summary = [("Total collaborators", report["total_collaborators"]), ("Combined strength", report["total_strength"])]
    sections = [
        ReportSection("Collaborators", ["Name", "Strength", "First collaboration", "Last collaboration"], [
            [c["name"], c["strength"], c["first_collaboration"], c["last_collaboration"]] for c in report["items"]
        ]),
    ]
    return _send_report("Collaborations Report", summary, sections, fmt, "collaborations_report")


@app.route("/reports/system")
@login_required
def report_system():
    access_token = session["access_token"]
    role = session.get("user_role", "")
    if (resp := _guard_report(role, "system")):
        return resp
    try:
        report = api_client.get_system_report(access_token)
        stats = dict(report)
        stats["users_by_role"] = _counts_to_dict(report["users_by_role"])
        stats["publications_by_status"] = _counts_to_dict(report["publications_by_status"])
        stats["projects_by_status"] = _counts_to_dict(report["projects_by_status"])
        stats["conferences_by_status"] = _counts_to_dict(report["conferences_by_status"])
    except ApiError as e:
        flash(f"Could not load system report: {e.detail}", "danger")
        stats = None
    return render_template("reports/system.html", stats=stats, role=role)


@app.route("/reports/system/export/<fmt>")
@login_required
def report_system_export(fmt):
    if fmt not in ("xlsx", "pdf"):
        abort(404)
    access_token = session["access_token"]
    role = session.get("user_role", "")
    if (resp := _guard_report(role, "system")):
        return resp
    try:
        report = api_client.get_system_report(access_token)
    except ApiError as e:
        flash(f"Could not load system report: {e.detail}", "danger")
        return redirect(url_for("report_system"))

    summary = [
        ("Total users", report["total_users"]), ("Total institutions", report["total_institutions"]),
        ("Total publications", report["total_publications"]), ("Total projects", report["total_projects"]),
        ("Total conferences", report["total_conferences"]), ("Total reviewers", report["total_reviewers"]),
    ]
    sections = [
        ReportSection("Users by role", ["Role", "Count"], [[d["label"], d["count"]] for d in report["users_by_role"]]),
        ReportSection("Publications by status", ["Status", "Count"], [[d["label"], d["count"]] for d in report["publications_by_status"]]),
        ReportSection("Projects by status", ["Status", "Count"], [[d["label"], d["count"]] for d in report["projects_by_status"]]),
        ReportSection("Conferences by status", ["Status", "Count"], [[d["label"], d["count"]] for d in report["conferences_by_status"]]),
    ]
    return _send_report("System Report", summary, sections, fmt, "system_report")


@app.route("/institution-admin/researchers")
@role_required("institution_admin")
def institution_admin_researchers():
    access_token = session["access_token"]
    institution_id = session.get("user_institution_id")
    affiliation_filter = request.args.get("affiliation_status") or None
    researchers = []
    if institution_id:
        try:
            researchers = api_client.list_all_users(
                access_token, institution_id=institution_id, role="researcher",
                affiliation_status=affiliation_filter, page_size=100,
            )
        except ApiError as e:
            flash(f"Could not load researchers: {e.detail}", "danger")
    return render_template(
        "institution_admin_researchers.html", researchers=researchers, affiliation_filter=affiliation_filter or ""
    )


@app.route("/institution-admin/researchers/<int:user_id>/approve", methods=["POST"])
@role_required("institution_admin")
def institution_admin_approve_researcher(user_id):
    access_token = session["access_token"]
    try:
        api_client.approve_affiliation(access_token, user_id)
        flash("Affiliation approved.", "success")
    except ApiError as e:
        flash(f"Could not approve affiliation: {e.detail}", "danger")
    return redirect(url_for("institution_admin_researchers"))


@app.route("/institution-admin/researchers/<int:user_id>/reject", methods=["POST"])
@role_required("institution_admin")
def institution_admin_reject_researcher(user_id):
    access_token = session["access_token"]
    try:
        api_client.reject_affiliation(access_token, user_id)
        flash("Affiliation rejected.", "info")
    except ApiError as e:
        flash(f"Could not reject affiliation: {e.detail}", "danger")
    return redirect(url_for("institution_admin_researchers"))


@app.route("/institution-admin/researchers/<int:user_id>/deactivate", methods=["POST"])
@role_required("institution_admin")
def institution_admin_deactivate_researcher(user_id):
    access_token = session["access_token"]
    try:
        api_client.deactivate_user(access_token, user_id)
        flash("Researcher deactivated.", "info")
    except ApiError as e:
        flash(f"Could not deactivate researcher: {e.detail}", "danger")
    return redirect(url_for("institution_admin_researchers"))


@app.route("/reviewer")
@role_required("reviewer")
def reviewer_dashboard():
    access_token = session["access_token"]
    try:
        reviews = api_client.list_my_reviews(access_token)
    except ApiError as e:
        flash(f"Could not load your reviews: {e.detail}", "danger")
        reviews = []
    counts = {"assigned": 0, "accepted": 0, "completed": 0, "declined": 0}
    for r in reviews:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    status_chart = donut_chart_data(counts)
    recent_reviews = sorted(reviews, key=lambda r: r.get("assigned_at") or "", reverse=True)[:6]
    return render_template(
        "reviewer_dashboard.html", counts=counts, reviews=reviews,
        status_chart=status_chart, recent_reviews=recent_reviews,
    )


@app.route("/reviewer/reviews")
@role_required("reviewer")
def reviewer_reviews():
    access_token = session["access_token"]
    status_filter = request.args.get("status") or None
    try:
        reviews = api_client.list_my_reviews(access_token, status=status_filter)
    except ApiError as e:
        flash(f"Could not load reviews: {e.detail}", "danger")
        reviews = []
    return render_template("reviewer_reviews.html", reviews=reviews, status_filter=status_filter or "")


@app.route("/reviewer/reviews/<int:review_id>")
@role_required("reviewer")
def review_detail(review_id):
    access_token = session["access_token"]
    try:
        review = api_client.get_review(access_token, review_id)
    except ApiError as e:
        flash(f"Could not load review: {e.detail}", "danger")
        return redirect(url_for("reviewer_reviews"))

    target = None
    if review["target_type"] == "publication":
        try:
            target = api_client.get_publication(access_token, review["target_id"])
        except ApiError:
            target = None

    return render_template("review_detail.html", review=review, target=target)


@app.route("/reviewer/reviews/<int:review_id>/accept", methods=["POST"])
@role_required("reviewer")
def accept_review_route(review_id):
    access_token = session["access_token"]
    try:
        api_client.accept_review(access_token, review_id)
        flash("Review accepted. You can now submit your evaluation.", "success")
    except ApiError as e:
        flash(f"Could not accept review: {e.detail}", "danger")
    return redirect(url_for("review_detail", review_id=review_id))


@app.route("/reviewer/reviews/<int:review_id>/decline", methods=["POST"])
@role_required("reviewer")
def decline_review_route(review_id):
    access_token = session["access_token"]
    try:
        api_client.decline_review(access_token, review_id)
        flash("Review declined.", "info")
    except ApiError as e:
        flash(f"Could not decline review: {e.detail}", "danger")
    return redirect(url_for("reviewer_reviews"))


@app.route("/reviewer/reviews/<int:review_id>/submit", methods=["POST"])
@role_required("reviewer")
def submit_review_route(review_id):
    access_token = session["access_token"]
    score = request.form.get("score", type=int)
    comments = request.form.get("comments") or None
    recommendation = request.form["recommendation"]
    try:
        api_client.submit_review(access_token, review_id, score, comments, recommendation)
        flash("Review submitted.", "success")
    except ApiError as e:
        flash(f"Could not submit review: {e.detail}", "danger")
    return redirect(url_for("review_detail", review_id=review_id))


@app.route("/projects")
@login_required
def projects():
    access_token = session["access_token"]
    mine = request.args.get("mine") == "true"
    ours = request.args.get("ours") == "true"
    institution_id = session.get("user_institution_id") if (ours and session.get("user_role") == "institution_admin") else None
    try:
        results = api_client.list_projects(access_token, mine=mine, institution_id=institution_id)
    except ApiError as e:
        flash(f"Could not load projects: {e.detail}", "danger")
        results = []
    return render_template("projects.html", projects=results, mine=mine, ours=ours)


@app.route("/projects/new", methods=["GET", "POST"])
@role_required("researcher", "institution_admin", "system_admin")
def new_project():
    access_token = session["access_token"]
    if request.method == "POST":
        data = {
            "title": request.form["title"],
            "description": request.form.get("description") or None,
            "start_date": request.form.get("start_date") or None,
            "end_date": request.form.get("end_date") or None,
        }
        lead_researcher_id = request.form.get("lead_researcher_id", type=int)
        if lead_researcher_id:
            data["lead_researcher_id"] = lead_researcher_id
        try:
            project = api_client.create_project(access_token, data)
            flash("Project created.", "success")
            return redirect(url_for("project_detail", project_id=project["project_id"]))
        except ApiError as e:
            flash(f"Could not create project: {e.detail}", "danger")
    return render_template("new_project.html")


@app.route("/projects/<int:project_id>")
@login_required
def project_detail(project_id):
    access_token = session["access_token"]
    try:
        project = api_client.get_project(access_token, project_id)
        members = api_client.list_project_members(access_token, project_id)
        account = api_client.get_my_account(access_token)
    except ApiError as e:
        flash(f"Could not load project: {e.detail}", "danger")
        return redirect(url_for("projects"))

    my_profile = None
    try:
        my_profile = api_client.get_my_researcher_profile(access_token)
    except ApiError:
        pass
    my_researcher_id = my_profile["researcher_id"] if my_profile else None

    is_lead = my_researcher_id is not None and project["lead_researcher_id"] == my_researcher_id
    is_manager = account["role"] == "system_admin" or (
        account["role"] == "institution_admin" and project.get("institution_id") == account.get("institution_id")
    )
    can_manage = is_lead or is_manager
    is_member = any(
        m["researcher_id"] == my_researcher_id and m["status"] == "accepted" for m in members
    )
    my_pending_invite = next(
        (m for m in members if m["researcher_id"] == my_researcher_id and m["status"] == "pending"), None,
    )

    invite_candidates = []
    if is_lead:
        existing_ids = {m["researcher_id"] for m in members}
        try:
            connections = api_client.list_my_collaborations(access_token, page=1, page_size=100)["items"]
        except ApiError:
            connections = []
        for c in connections:
            partner = c.get("partner")
            if partner and partner["researcher_id"] not in existing_ids:
                invite_candidates.append(partner)

    messages = []
    if is_member or can_manage:
        try:
            messages = api_client.list_project_messages(access_token, project_id)["items"]
        except ApiError as e:
            flash(f"Could not load project chat: {e.detail}", "danger")

    return render_template(
        "project_detail.html", project=project, members=members, can_manage=can_manage,
        is_member=is_member, my_researcher_id=my_researcher_id, my_pending_invite=my_pending_invite,
        invite_candidates=invite_candidates, messages=messages,
    )


@app.route("/projects/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    access_token = session["access_token"]
    if request.method == "POST":
        data = {
            "title": request.form["title"],
            "description": request.form.get("description") or None,
            "status": request.form["status"],
            "start_date": request.form.get("start_date") or None,
            "end_date": request.form.get("end_date") or None,
        }
        try:
            api_client.update_project(access_token, project_id, data)
            flash("Project updated.", "success")
            return redirect(url_for("project_detail", project_id=project_id))
        except ApiError as e:
            flash(f"Could not update project: {e.detail}", "danger")
    try:
        project = api_client.get_project(access_token, project_id)
    except ApiError as e:
        flash(f"Could not load project: {e.detail}", "danger")
        return redirect(url_for("projects"))
    return render_template("edit_project.html", project=project)


@app.route("/projects/<int:project_id>/delete", methods=["POST"])
@login_required
def delete_project(project_id):
    access_token = session["access_token"]
    try:
        api_client.delete_project(access_token, project_id)
        flash("Project deleted.", "info")
    except ApiError as e:
        flash(f"Could not delete project: {e.detail}", "danger")
        return redirect(url_for("project_detail", project_id=project_id))
    return redirect(url_for("projects"))


@app.route("/projects/<int:project_id>/members/add", methods=["POST"])
@login_required
def add_project_member(project_id):
    access_token = session["access_token"]
    researcher_id = request.form.get("researcher_id", type=int)
    try:
        api_client.add_project_member(access_token, project_id, researcher_id)
        flash("Member added.", "success")
    except ApiError as e:
        flash(f"Could not add member: {e.detail}", "danger")
    return redirect(url_for("project_detail", project_id=project_id))


@app.route("/projects/<int:project_id>/members/<int:researcher_id>/remove", methods=["POST"])
@login_required
def remove_project_member(project_id, researcher_id):
    access_token = session["access_token"]
    try:
        api_client.remove_project_member(access_token, project_id, researcher_id)
        flash("Member removed.", "info")
    except ApiError as e:
        flash(f"Could not remove member: {e.detail}", "danger")
    return redirect(url_for("project_detail", project_id=project_id))

@app.route("/projects/<int:project_id>/members/<int:project_member_id>/respond", methods=["POST"])
@login_required
def respond_to_project_invitation(project_id, project_member_id):
    access_token = session["access_token"]
    accept = request.form.get("accept") == "true"
    try:
        api_client.respond_to_project_invitation(access_token, project_id, project_member_id, accept)
        flash("You joined the project." if accept else "Invitation declined.", "success" if accept else "info")
    except ApiError as e:
        flash(f"Could not respond to invitation: {e.detail}", "danger")
    return redirect(url_for("project_detail", project_id=project_id))


@app.route("/projects/<int:project_id>/messages", methods=["POST"])
@login_required
def send_project_message_route(project_id):
    access_token = session["access_token"]
    body = request.form.get("body", "")
    try:
        api_client.send_project_message(access_token, project_id, body)
    except ApiError as e:
        flash(f"Could not send message: {e.detail}", "danger")
    return redirect(url_for("project_detail", project_id=project_id) + "#project-chat-end")


@app.route("/notifications")
@login_required
def notifications():
    access_token = session["access_token"]
    unread_only = request.args.get("unread_only") == "true"
    page = request.args.get("page", 1, type=int)
    try:
        result = api_client.list_notifications(access_token, unread_only=unread_only, page=page)
    except ApiError as e:
        flash(f"Could not load notifications: {e.detail}", "danger")
        result = {"items": [], "total": 0, "unread_count": 0, "page": page, "page_size": 20}

    # Fetch pending incoming requests so the template can render
    # Accept/Reject buttons directly on collaboration_request_received
    # notifications without parsing link_url or creating a combined route
    pending_requests_by_name = {}
    try:
        reqs = api_client.list_collaboration_requests(access_token, direction="incoming", status_filter="pending")
        for r in reqs.get("items", []):
            key = f"{r['requester']['first_name']} {r['requester']['last_name']}"
            pending_requests_by_name[key] = r["collaboration_request_id"]
    except ApiError:
        pass

    return render_template(
        "notifications.html",
        result=result,
        unread_only=unread_only,
        page=page,
        pending_requests_by_name=pending_requests_by_name,
    )

@app.route("/notifications/<int:notification_id>/read", methods=["POST"])
@login_required
def mark_notification_read(notification_id):
    access_token = session["access_token"]
    try:
        api_client.mark_notification_read(access_token, notification_id)
    except ApiError as e:
        flash(f"Could not update notification: {e.detail}", "danger")
    return redirect(request.referrer or url_for("notifications"))


@app.route("/notifications/mark-all-read", methods=["POST"])
@login_required
def mark_all_notifications_read():
    access_token = session["access_token"]
    try:
        api_client.mark_all_notifications_read(access_token)
        flash("All notifications marked as read.", "success")
    except ApiError as e:
        flash(f"Could not update notifications: {e.detail}", "danger")
    return redirect(url_for("notifications"))


@app.route("/notifications/<int:notification_id>/delete", methods=["POST"])
@login_required
def delete_notification(notification_id):
    access_token = session["access_token"]
    try:
        api_client.delete_notification(access_token, notification_id)
    except ApiError as e:
        flash(f"Could not delete notification: {e.detail}", "danger")
    return redirect(url_for("notifications"))

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "")
        try:
            result = api_client.forgot_password(email)
            flash(result.get("message", "If that email has an account, a reset link has been sent."), "info")
        except ApiError as e:
            flash(f"Could not process request: {e.detail}", "danger")
        return redirect(url_for("login"))
    return render_template("forgot_password.html")


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    token = request.args.get("token") or request.form.get("token")
    if not token:
        flash("Missing password reset token.", "danger")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")
        if new_password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("reset_password.html", token=token)
        try:
            result = api_client.reset_password(token, new_password)
            flash(result.get("message", "Password reset successfully."), "success")
            return redirect(url_for("login"))
        except ApiError as e:
            flash(f"Could not reset password: {e.detail}", "danger")
            return render_template("reset_password.html", token=token)

    return render_template("reset_password.html", token=token)


@app.route("/chatbot/message", methods=["POST"])
@login_required
def chatbot_message():
    """AJAX endpoint the chat widget posts to. The browser keeps the
    conversation history and resends it each call (see static/js/chatbot.js)
    -- this route just forwards it to the backend, which does the actual
    FAQ-answering and live-data lookups."""
    access_token = session["access_token"]
    data = request.get_json(silent=True) or {}
    messages = data.get("messages", [])
    if not isinstance(messages, list) or not messages:
        return {"error": "No message provided."}, 400
    try:
        result = api_client.send_chat_message(access_token, messages)
        return result
    except ApiError as e:
        return {"error": e.detail if isinstance(e.detail, str) else "The chatbot is unavailable right now."}, e.status_code


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)