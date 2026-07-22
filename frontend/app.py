from functools import wraps

import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash, Response

import api_client
from api_client import ApiError
from config import FLASK_SECRET_KEY

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "access_token" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapped


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
        try:
            api_client.register(email, password, role, institution_id)
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
    return render_template("register.html", institutions=institutions)


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


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        try:
            tokens = api_client.login(email, password)
            session["access_token"] = tokens["access_token"]
            session["refresh_token"] = tokens["refresh_token"]
            flash("Logged in successfully.", "success")
            return redirect(url_for("dashboard"))
        except ApiError as e:
            flash(f"Login failed: {e.detail}", "danger")
    return render_template("login.html")


@app.route("/auth/google-session", methods=["POST"])
def google_session():
    """
    Called by the client-side Google Sign-In JS after it has already
    exchanged the Google id_token for our own access/refresh tokens via
    FastAPI's /auth/google. This just stores those tokens into Flask's
    server-side session, the same way the normal /login route does, so
    that login_required and the rest of the app work identically
    regardless of which sign-in method was used.
    """
    data = request.get_json(silent=True) or {}
    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token")
    if not access_token or not refresh_token:
        return {"error": "Missing tokens"}, 400
    session["access_token"] = access_token
    session["refresh_token"] = refresh_token
    return {"ok": True}


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    access_token = session["access_token"]
    try:
        account = api_client.get_my_account(access_token)
    except ApiError as e:
        if e.status_code == 401:
            session.clear()
            flash("Your session expired. Please log in again.", "warning")
            return redirect(url_for("login"))
        flash(f"Could not load account: {e.detail}", "danger")
        account = None

    profile = None
    if account and account["role"] == "researcher":
        profile = api_client.get_my_researcher_profile(access_token)

    return render_template("dashboard.html", account=account, profile=profile)


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
    if page_size not in (10, 25, 50):
        page_size = 10
    try:
        result = api_client.list_publications(access_token, page=page, page_size=page_size)
    except ApiError as e:
        flash(f"Could not load publications: {e.detail}", "danger")
        result = {"items": [], "total": 0, "page": page, "page_size": page_size}
    return render_template("publications.html", result=result, page=page, page_size=page_size)


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


@app.route("/publications/<int:publication_id>")
@login_required
def publication_detail(publication_id):
    access_token = session["access_token"]
    try:
        publication = api_client.get_publication(access_token, publication_id)
    except ApiError as e:
        flash(f"Could not load publication: {e.detail}", "danger")
        return redirect(url_for("publications"))
    return render_template("publication_detail.html", publication=publication)


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


@app.route("/publications/<int:publication_id>/download")
@login_required
def download_publication(publication_id):
    access_token = session["access_token"]
    resp = requests.get(
        f"{api_client.BACKEND_API_URL}/publications/{publication_id}/download",
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
    try:
        results = api_client.list_conferences(access_token)
    except ApiError as e:
        flash(f"Could not load conferences: {e.detail}", "danger")
        results = []
    return render_template("conferences.html", conferences=results)


@app.route("/conferences/new", methods=["GET", "POST"])
@login_required
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
@login_required
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
    except ApiError as e:
        flash(f"Could not load conference: {e.detail}", "danger")
        return redirect(url_for("conferences"))
    my_researcher_id = my_profile["researcher_id"] if my_profile else None
    return render_template(
        "conference_detail.html", conference=conference, participants=participants, my_researcher_id=my_researcher_id
    )


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
    data = {
        "role": request.form["role"],
        "presentation_title": request.form.get("presentation_title") or None,
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
    return render_template("directory.html", results=results, skill=skill or "", interest=interest or "")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
