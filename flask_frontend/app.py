from flask import Flask, render_template, request, redirect, url_for, session
import requests


app = Flask(__name__)

app.secret_key = "scientific-collaboration-secret"


API_URL = "http://127.0.0.1:8000"



# ---------------------- Home ----------------------

@app.route("/")
def home():

    return redirect(url_for("login"))




# ---------------------- Login ----------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":


        email = request.form.get("email")
        password = request.form.get("password")


        try:

            response = requests.post(

                f"{API_URL}/login",

                data={
                    "username": email,
                    "password": password
                }

            )


            print("LOGIN STATUS:", response.status_code)
            print("LOGIN RESPONSE:", response.text)



            if response.status_code == 200:


                data = response.json()

                print("LOGIN DATA:", data)
                session["token"] = data["access_token"]

                session["email"] = data["email"]

                session["full_name"] = data["full_name"]

                session["role"] = data["role"]
                session["user_id"] = data["user_id"]

                print("LOGIN USER:", data["email"])
                print("LOGIN ROLE:", data["role"])
                session["researcher_id"] = data.get("researcher_id")

                return redirect(
                    url_for("dashboard")
                )



            # Handle JSON / Non JSON response

            try:

                error_message = response.json().get(
                    "detail",
                    "Invalid Email or Password"
                )


            except ValueError:

                error_message = response.text



            return render_template(
                "login.html",
                error=error_message
            )



        except requests.exceptions.ConnectionError:


            return render_template(
                "login.html",
                error="Backend server is not running."
            )



    return render_template("login.html")






# ---------------------- Register ----------------------

@app.route("/register", methods=["GET", "POST"])
def register():


    if request.method == "POST":


        full_name = request.form.get("full_name")

        email = request.form.get("email")

        password = request.form.get("password")

        confirm_password = request.form.get("confirm_password")

        role = request.form.get("role")



        if password != confirm_password:


            return render_template(

                "register.html",

                error="Passwords do not match"

            )



        try:


            response = requests.post(

                f"{API_URL}/register",

                json={

                    "full_name": full_name,

                    "email": email,

                    "password": password,

                    "role": role

                }

            )



            print("REGISTER STATUS:", response.status_code)

            print("REGISTER RESPONSE:", response.text)



            if response.status_code == 200:


                return redirect(
                    url_for("login")
                )



            try:

                error_message = response.json().get(

                    "detail",

                    "Registration failed"

                )


            except ValueError:

                error_message = response.text



            return render_template(

                "register.html",

                error=error_message

            )



        except requests.exceptions.ConnectionError:


            return render_template(

                "register.html",

                error="Backend server is not running."

            )



    return render_template("register.html")






# ---------------------- Dashboard ----------------------
@app.route("/dashboard")
def dashboard():

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    researcher_count = 0
    publication_count = 0
    institution_count = 0
    conference_count = 0


    # Researchers count
    response = requests.get(
        f"{API_URL}/researchers/",
        headers=headers
    )

    if response.status_code == 200:
        researchers = response.json()
        researcher_count = len(researchers)



    # Publications count

    if session["role"] == "researcher":

        response = requests.get(
            f"{API_URL}/publications/user/{session['user_id']}",
            headers=headers
        )

    else:

        response = requests.get(
            f"{API_URL}/publications/",
            headers=headers
        )


    if response.status_code == 200:

        publications = response.json()
        publication_count = len(publications)



    return render_template(
        "dashboard.html",

        role=session["role"],

        name=session["full_name"],

        researcher_count=researcher_count,

        publication_count=publication_count,

        institution_count=institution_count,

        conference_count=conference_count
    )
# ---------------------- Researchers ----------------------

@app.route("/researchers")
def researchers():

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    response = requests.get(
        f"{API_URL}/researchers/",
        headers=headers
    )


    researchers = []


    if response.status_code == 200:
        researchers = response.json()


    return render_template(
        "researchers.html",
        researchers=researchers
    )






# ---------------------- Add Researcher ----------------------

@app.route("/researchers/add", methods=["POST"])
def add_researcher():


    if "token" not in session:

        return redirect(
            url_for("login")
        )



    data = {


        "full_name": request.form.get("full_name"),

        "email": request.form.get("email"),

        "department": request.form.get("department"),

        "institution": request.form.get("institution"),

        "designation": request.form.get("designation"),

        "research_interests": request.form.get("research_interests"),

        "skills": None,

        "phone": None

    }



    headers = {


        "Authorization":
        f"Bearer {session['token']}"

    }




    response = requests.post(

        f"{API_URL}/researchers/",

        json=data,

        headers=headers

    )



    print("ADD RESEARCHER STATUS:", response.status_code)

    print("ADD RESEARCHER RESPONSE:", response.text)



    if response.status_code == 200:


        return redirect(
            url_for("researchers")
        )



    try:

        error_message = response.json().get(

            "detail",

            "Failed to add researcher"

        )


    except ValueError:

        error_message = response.text



    return render_template(

        "researchers.html",

        error=error_message

    )

# ---------------------- Delete Researcher ----------------------

@app.route("/researchers/delete/<int:researcher_id>")
def delete_researcher(researcher_id):

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    response = requests.delete(
        f"{API_URL}/researchers/{researcher_id}",
        headers=headers
    )


    if response.status_code == 200:

        session["message"] = "Researcher deleted successfully"


    else:

        session["message"] = "Failed to delete researcher"



    return redirect(
        url_for("researchers")
    )

# ---------------------- Edit Researcher ----------------------

@app.route("/researchers/edit/<int:researcher_id>", methods=["GET","POST"])
def edit_researcher(researcher_id):

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    if request.method == "POST":


        data = {

            "full_name": request.form.get("full_name"),

            "email": request.form.get("email"),

            "department": request.form.get("department"),

            "institution": request.form.get("institution"),

            "designation": request.form.get("designation"),

            "research_interests": request.form.get("research_interests"),

            "skills": request.form.get("skills"),

            "phone": request.form.get("phone")

        }


        response = requests.put(

            f"{API_URL}/researchers/{researcher_id}",

            json=data,

            headers=headers

        )


        print(response.status_code)
        print(response.text)


        return redirect(
            url_for("researchers")
        )



    # Get existing researcher data

    response = requests.get(

        f"{API_URL}/researchers/{researcher_id}",

        headers=headers

    )


    researcher = response.json()


    return render_template(

        "edit_researcher.html",

        researcher=researcher

    )

# ---------------- Researcher Profile ----------------

# ---------------- Researcher Profile ----------------

@app.route("/researcher/profile", methods=["GET", "POST"])
def researcher_profile():

    if "token" not in session:
        return redirect(url_for("login"))

    headers = {
        "Authorization": f"Bearer {session['token']}"
    }

    # ---------- SAVE / UPDATE PROFILE ----------
    if request.method == "POST":

        data = {

            "institution": request.form.get("institution"),
            "department": request.form.get("department"),
            "designation": request.form.get("designation"),
            "research_interests": request.form.get("research_interests"),
            "skills": request.form.get("skills"),
            "phone": request.form.get("phone")

        }

        # Check if profile already exists
        check_response = requests.get(

            f"{API_URL}/researchers/profile/me",

            headers=headers

        )

        if check_response.status_code == 200:

            # Profile exists -> Update
            response = requests.put(

                f"{API_URL}/researchers/profile",

                json=data,

                headers=headers

            )

        else:

            # Profile doesn't exist -> Create
            response = requests.post(

                f"{API_URL}/researchers/profile",

                json=data,

                headers=headers

            )

        if response.status_code == 200:

            return redirect(
                url_for("researcher_profile")
            )

        return render_template(
            "profile.html",
            error=response.json().get("detail")
        )

    # ---------- CHECK EXISTING PROFILE ----------

    response = requests.get(

        f"{API_URL}/researchers/profile/me",

        headers=headers

    )

    print("SESSION EMAIL:", session["email"])
    print("PROFILE STATUS:", response.status_code)
    print("PROFILE RESPONSE:", response.text)

    if response.status_code == 200:

        researcher = response.json()

        return render_template(

            "profile_view.html",

            researcher=researcher

        )

    # ---------- NO PROFILE CREATED ----------

    return render_template(
        "profile.html"
    )

# ---------------------- Publications ----------------------

# ---------------------- Publications ----------------------

@app.route("/publications")
def publications():

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    publications = []


    # ---------------- Get Publications ----------------

    if session["role"] == "researcher":

        response = requests.get(
            f"{API_URL}/publications/user/{session['user_id']}",
            headers=headers
        )

    else:

        response = requests.get(
            f"{API_URL}/publications/",
            headers=headers
        )


    if response.status_code == 200:
        publications = response.json()



    # ---------------- Get Researchers ----------------
    # Researcher -> only their own name
    # Admin -> all researchers

    researchers = []


    if session["role"] == "researcher":

        response = requests.get(
            f"{API_URL}/researchers/user/{session['user_id']}",
            headers=headers
        )
        print("USER ID:", session["user_id"])
        print("RESEARCHER RESPONSE:", response.text)

        if response.status_code == 200:

            researchers = [
                response.json()
            ]


    else:

        response = requests.get(
            f"{API_URL}/researchers/",
            headers=headers
        )


        if response.status_code == 200:

            researchers = response.json()



    return render_template(
        "publications.html",
        publications=publications,
        researchers=researchers
    )
@app.route("/publication/add", methods=["POST"])
def add_publication():

    if "token" not in session:
        return redirect(url_for("login"))

    print("FORM DATA:", request.form)
    print("Researcher ID:", request.form.get("researcher_id"))
    print("Session:", session)

    researcher_id = request.form.get("researcher_id")

    if not researcher_id:
        return "Researcher ID is missing!", 400


    data = {
        "researcher_id": int(researcher_id),
        "title": request.form.get("title"),
        "publication_type": request.form.get("publication_type"),
        "journal_name": request.form.get("journal_name"),
        "conference_name": request.form.get("conference_name"),
        "publication_year": request.form.get("publication_year"),
        "doi": request.form.get("doi"),
        "status": request.form.get("status")
    }


    files = None

    if "publication_file" in request.files:

        pdf = request.files["publication_file"]

        if pdf.filename != "":
            files = {
                "file": (
                    pdf.filename,
                    pdf.stream,
                    "application/pdf"
                )
            }


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    response = requests.post(
        f"{API_URL}/publications/",
        data=data,
        files=files,
        headers=headers
    )


    print("ADD PUBLICATION:", response.status_code)
    print(response.text)


    return redirect(url_for("publications"))
@app.route("/publication/delete/<int:id>")
def delete_publication(id):

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    requests.delete(

        f"{API_URL}/publications/{id}",

        headers=headers

    )


    return redirect(
        url_for("publications")
    )
@app.route("/publication/edit/<int:id>", methods=["GET","POST"])
@app.route("/publication/edit/<int:id>", methods=["GET", "POST"])
def edit_publication(id):

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    if request.method == "POST":


        data = {

            "researcher_id": int(request.form.get("researcher_id")),

            "title": request.form.get("title"),

            "publication_type": request.form.get("publication_type"),

            "journal_name": request.form.get("journal_name"),

            "conference_name": request.form.get("conference_name"),

            "publication_year": int(request.form.get("publication_year")),

            "doi": request.form.get("doi"),

            "status": request.form.get("status")

        }


        files = None


        if "publication_file" in request.files:

            pdf = request.files["publication_file"]


            if pdf.filename != "":

                files = {

                    "file": (

                        pdf.filename,

                        pdf.stream,

                        "application/pdf"

                    )

                }


        response = requests.put(

            f"{API_URL}/publications/{id}",

            data=data,

            files=files,

            headers=headers

        )


        print("UPDATE PUBLICATION:", response.status_code)
        print(response.text)


        return redirect(
            url_for("publications")
        )



    response = requests.get(

        f"{API_URL}/publications/{id}",

        headers=headers

    )


    publication = response.json()


    return render_template(

        "publication_form.html",

        publication=publication

    )
# ---------------------- Conferences ----------------------

@app.route("/conferences")
def conferences():

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    response = requests.get(
        f"{API_URL}/conferences/",
        headers=headers
    )


    conferences = []


    if response.status_code == 200:
        conferences = response.json()


    return render_template(
        "conferences.html",
        conferences=conferences
    )



# ---------------------- Add Conference ----------------------

@app.route("/conference/add", methods=["POST"])
def add_conference():


    if "token" not in session:
        return redirect(url_for("login"))


    data = {

        "title": request.form.get("title"),

        "organizer": request.form.get("organizer"),

        "location": request.form.get("location"),

        "conference_date": request.form.get("conference_date"),

        "website": request.form.get("website")

    }



    headers = {

        "Authorization":
        f"Bearer {session['token']}"

    }



    response = requests.post(

        f"{API_URL}/conferences/",

        json=data,

        headers=headers

    )


    print("ADD CONFERENCE:", response.status_code)
    print(response.text)


    return redirect(
        url_for("conferences")
    )

# ---------------------- Logout ----------------------

@app.route("/logout")
def logout():


    session.clear()


    return redirect(
        url_for("login")
    )





# ---------------------- Run Flask ----------------------

if __name__ == "__main__":

    app.run(debug=True)