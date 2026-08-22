"""
Flask frontend for the Scientific Collaboration Network Analyzer (Milestone 1).

Wired to the FastAPI backend: login/register/profile now call the real API
and store the JWT access token in the Flask session.
"""
import os

import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")

BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")


def _auth_headers() -> dict:
    token = session.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}


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
            flash("Incorrect email or password.", "error")
            return redirect(url_for("login"))

        data = resp.json()
        session["token"] = data["access_token"]
        session["email"] = email
        flash("Logged in successfully.", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        role = request.form.get("role", "researcher")
        try:
            resp = requests.post(
                f"{BACKEND_URL}/auth/register",
                json={"email": email, "password": password, "role": role},
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
    return render_template("dashboard.html", user=user)


@app.route("/profile", methods=["GET", "POST"])
def profile():
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


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
