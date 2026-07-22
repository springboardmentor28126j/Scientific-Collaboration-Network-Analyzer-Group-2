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
                session["role"] = data.get("role", "researcher")
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

    role = session.get("role", "researcher")

    # Researcher ka naam fetch karo
    display_name = session.get("email")
    try:
        response = requests.get(f"{API_URL}/researchers/")
        if response.status_code == 200:
            researchers = response.json()
            if researchers:
                display_name = researchers[-1]["full_name"]
    except requests.exceptions.ConnectionError:
        pass

    # Publications count aur recent list fetch karo
    pub_count = 0
    recent_pubs = []
    try:
        response = requests.get(f"{API_URL}/publications/")
        if response.status_code == 200:
            pubs = response.json()
            pub_count = len(pubs)
            recent_pubs = pubs[-3:]  # sabse recent 3
    except requests.exceptions.ConnectionError:
        pass

    # Conferences count fetch karo
    conf_count = 0
    try:
        response = requests.get(f"{API_URL}/conferences/")
        if response.status_code == 200:
            confs = response.json()
            conf_count = len(confs)
    except requests.exceptions.ConnectionError:
        pass

    if role == "institution_admin":
        return render_template("dashboard_institution.html", email=session.get("email"), display_name=display_name)
    elif role == "system_admin":
        return render_template("dashboard_admin.html", email=session.get("email"), display_name=display_name)
    else:
        return render_template(
            "dashboard.html",
            email=session.get("email"),
            display_name=display_name,
            pub_count=pub_count,
            conf_count=conf_count,
            recent_pubs=recent_pubs
        )  
@app.route("/publications")
def publications():
    if "token" not in session:
        return redirect(url_for("login"))

    try:
        response = requests.get(f"{API_URL}/publications/")
        pubs = response.json() if response.status_code == 200 else []
    except requests.exceptions.ConnectionError:
        pubs = []

    return render_template("publications.html", publications=pubs)


@app.route("/publications/add", methods=["GET", "POST"])
def add_publication():
    if "token" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form.get("title")
        pub_type = request.form.get("type")
        doi = request.form.get("doi")
        uploaded_file = request.files.get("file")

        try:
            response = requests.post(
                f"{API_URL}/publications/",
                json={
                    "title": title,
                    "type": pub_type,
                    "doi": doi if doi else None,
                    "author_id": 1
                }
            )

            if response.status_code == 200:
                new_pub = response.json()
                pub_id = new_pub["id"]

                # Agar file select kiya hai to usko upload karo
                if uploaded_file and uploaded_file.filename:
                    files = {"file": (uploaded_file.filename, uploaded_file.stream, uploaded_file.mimetype)}
                    requests.post(f"{API_URL}/publications/{pub_id}/upload", files=files)

                return redirect(url_for("publications"))
            else:
                return render_template("add_publication.html", error="Something went wrong")
        except requests.exceptions.ConnectionError:
            return render_template("add_publication.html", error="Cannot connect to server")

    return render_template("add_publication.html")

@app.route("/conferences")
def conferences():
    if "token" not in session:
        return redirect(url_for("login"))

    try:
        response = requests.get(f"{API_URL}/conferences/")
        confs = response.json() if response.status_code == 200 else []
    except requests.exceptions.ConnectionError:
        confs = []

    return render_template("conferences.html", conferences=confs)


@app.route("/conferences/add", methods=["GET", "POST"])
def add_conference():
    if "token" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form.get("name")
        location = request.form.get("location")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        try:
            response = requests.post(
                f"{API_URL}/conferences/",
                json={
                    "name": name,
                    "location": location,
                    "start_date": start_date if start_date else None,
                    "end_date": end_date if end_date else None
                }
            )
            if response.status_code == 200:
                return redirect(url_for("conferences"))
            else:
                return render_template("add_conference.html", error="Something went wrong")
        except requests.exceptions.ConnectionError:
            return render_template("add_conference.html", error="Cannot connect to server")

    return render_template("add_conference.html")  

@app.route("/institutions")
def institutions():
    if "token" not in session:
        return redirect(url_for("login"))

    try:
        response = requests.get(f"{API_URL}/institutions/")
        insts = response.json() if response.status_code == 200 else []
    except requests.exceptions.ConnectionError:
        insts = []

    return render_template("institutions.html", institutions=insts)


@app.route("/institutions/add", methods=["GET", "POST"])
def add_institution():
    if "token" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form.get("name")
        inst_type = request.form.get("type")
        location = request.form.get("location")
        website = request.form.get("website")
        description = request.form.get("description")

        try:
            response = requests.post(
                f"{API_URL}/institutions/",
                json={
                    "name": name,
                    "type": inst_type,
                    "location": location,
                    "website": website if website else None,
                    "description": description if description else None
                }
            )
            if response.status_code == 200:
                return redirect(url_for("institutions"))
            else:
                return render_template("add_institution.html", error="Something went wrong")
        except requests.exceptions.ConnectionError:
            return render_template("add_institution.html", error="Cannot connect to server")

    return render_template("add_institution.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)