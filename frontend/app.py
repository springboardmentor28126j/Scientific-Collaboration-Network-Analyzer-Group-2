from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = "your-secret-key-change-this"

API_URL = "http://127.0.0.1:8000"


@app.route("/")
def home():
    return render_template("landing.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        try:
            response = requests.post(
                f"{API_URL}/auth/login",
                params={"email": email, "password": password}
            )

            if response.status_code == 200:
                data = response.json()
                session["token"] = data["access_token"]
                session["email"] = email
                return redirect(url_for("dashboard"))
            else:
                return render_template("login.html", error="Invalid email or password")

        except requests.exceptions.ConnectionError:
            return render_template("login.html", error="Cannot connect to server")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm_password")
        role = request.form.get("role")

        if password != confirm:
            return render_template("register.html", error="Passwords do not match")

        try:
            response = requests.post(
                f"{API_URL}/auth/register",
                json={"email": email, "password": password, "role": role}
            )

            if response.status_code == 200:
                return redirect(url_for("login"))
            elif response.status_code == 400:
                return render_template("register.html", error="Email already registered")
            else:
                return render_template("register.html", error="Something went wrong")

        except requests.exceptions.ConnectionError:
            return render_template("register.html", error="Cannot connect to server")

    return render_template("register.html")


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "token" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        full_name = request.form.get("full_name")
        department = request.form.get("department")
        institution = request.form.get("institution")
        interests = request.form.get("interests")
        skills = request.form.get("skills")

        try:
            response = requests.post(
                f"{API_URL}/researchers/",
                json={
                    "full_name": full_name,
                    "department": department,
                    "institution": institution,
                    "research_interests": interests,
                    "skills": skills
                }
            )

            if response.status_code == 200:
                return redirect(url_for("dashboard"))
            else:
                return render_template("profile.html", error="Something went wrong")

        except requests.exceptions.ConnectionError:
            return render_template("profile.html", error="Cannot connect to server")

    return render_template("profile.html")


@app.route("/dashboard")
def dashboard():
    if "token" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html", email=session.get("email"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)