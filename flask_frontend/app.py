from flask import Flask, render_template, request, redirect, url_for, session
import requests
from datetime import datetime


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
                session["institution"] = data.get("institution")

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

        institution_name = request.form.get("institution_name")


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

                    "role": role,

                    "institution_name": institution_name

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
    department_count = 0
    conference_count = 0



    # ================= INSTITUTION ADMIN =================

    if session["role"] == "institution_admin":


        # -------- Researchers --------

        response = requests.get(
            f"{API_URL}/researchers/",
            headers=headers
        )


        researchers = []


        if response.status_code == 200:

            researchers = response.json()


            # Only this institution researchers

            researchers = [

                r for r in researchers

                if r.get("institution") == session.get("institution")

            ]


            researcher_count = len(researchers)



        # -------- Publications --------

        response = requests.get(
            f"{API_URL}/publications/",
            headers=headers
        )


        if response.status_code == 200:


            publications = response.json()


            institution_researcher_ids = [

                r["id"]

                for r in researchers

            ]


            publications = [

                p for p in publications

                if p.get("researcher_id") 
                in institution_researcher_ids

            ]


            publication_count = len(publications)



        # -------- Departments --------

        departments = set()


        for r in researchers:

            if r.get("department"):

                departments.add(
                    r.get("department")
                )


        department_count = len(departments)



        # -------- Conferences --------

        response = requests.get(
            f"{API_URL}/conferences/",
            headers=headers
        )


        if response.status_code == 200:


            conferences = response.json()


            conferences = [

                c for c in conferences

                if c.get("institution") == session.get("institution")

            ]


            conference_count = len(conferences)





    # ================= RESEARCHER =================

    elif session["role"] == "researcher":


        response = requests.get(
            f"{API_URL}/publications/user/{session['user_id']}",
            headers=headers
        )


        if response.status_code == 200:

            publications = response.json()

            publication_count = len(publications)



        response = requests.get(
            f"{API_URL}/conferences/",
            headers=headers
        )


        if response.status_code == 200:

            conferences = response.json()

            conference_count = len(conferences)





    # ================= SYSTEM ADMIN =================

    elif session["role"] == "system_admin":


        # Researchers

        response = requests.get(
            f"{API_URL}/researchers/",
            headers=headers
        )


        if response.status_code == 200:

            researchers = response.json()

            researcher_count = len(researchers)




        # Publications

        response = requests.get(
            f"{API_URL}/publications/",
            headers=headers
        )


        if response.status_code == 200:

            publications = response.json()

            publication_count = len(publications)




        # Conferences

        response = requests.get(
            f"{API_URL}/conferences/",
            headers=headers
        )


        if response.status_code == 200:

            conferences = response.json()

            conference_count = len(conferences)





    return render_template(

        "dashboard.html",

        role=session["role"],

        name=session["full_name"],

        researcher_count=researcher_count,

        publication_count=publication_count,

        department_count=department_count,

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


    # Get all researchers from backend

    response = requests.get(
        f"{API_URL}/researchers/",
        headers=headers
    )


    researchers = []


    if response.status_code == 200:

        researchers = response.json()


        print("ALL RESEARCHERS:", researchers)
        print("USER ROLE:", session.get("role"))
        print("SESSION INSTITUTION:", session.get("institution"))



        # Institution Admin -> show only own institution researchers

        if session.get("role") == "institution_admin":


            institution_name = session.get("institution")


            researchers = [

                r for r in researchers

                if r.get("institution") == institution_name

            ]


            print("FILTERED RESEARCHERS:", researchers)



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
@app.route("/institution/profile", methods=["GET", "POST"])
def institution_profile():

    if "token" not in session:
        return redirect(url_for("login"))

    headers = {
        "Authorization": f"Bearer {session['token']}"
    }

    # ---------- SAVE / UPDATE PROFILE ----------
    if request.method == "POST":

        data = {

            "institution_type": request.form.get("institution_type"),
            "location": request.form.get("location"),
            "website": request.form.get("website"),
            "phone": request.form.get("phone")

        }

        print("FORM DATA:", data)

        # Check if profile already exists
        check_response = requests.get(
            f"{API_URL}/institutions/profile/me",
            headers=headers
        )

        if check_response.status_code == 200:

            # Profile exists -> Update
            response = requests.put(
                f"{API_URL}/institutions/profile",
                json=data,
                headers=headers
            )
            print(response.status_code)
            print(response.text)

        else:

            # Profile doesn't exist -> Create
            response = requests.post(
                f"{API_URL}/institutions/profile",
                json=data,
                headers=headers
            )

        print("UPDATE STATUS:", response.status_code)
        print("UPDATE RESPONSE:", response.text)

        if response.status_code in [200, 201]:

            return redirect(
                url_for("institution_profile")
            )

        return render_template(
            "profile.html",
            institution=data,
            error=response.json().get(
                "detail",
                "Profile save failed"
            )
        )

    # ---------- CHECK EXISTING PROFILE ----------

    response = requests.get(
        f"{API_URL}/institutions/profile/me",
        headers=headers
    )

    print("INSTITUTION STATUS:", response.status_code)
    print("INSTITUTION RESPONSE:", response.text)

    if response.status_code == 200:

        institution = response.json()

        return render_template(
            "profile_view.html",
            institution=institution
        )

    return render_template(
        "profile.html",
        institution=None
    )
# ---------------------- Publications ----------------------

@app.route("/publications")
def publications():

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    publications = []
    researchers = []


    # ================= GET RESEARCHERS =================


    response = requests.get(
        f"{API_URL}/researchers/",
        headers=headers
    )


    if response.status_code == 200:

        all_researchers = response.json()



        # Researcher -> only himself

        if session["role"] == "researcher":

            researchers = [

                r for r in all_researchers

                if r["user_id"] == session["user_id"]

            ]



        # Institution Admin -> only his institution researchers

        elif session["role"] == "institution_admin":


            researchers = [

                r for r in all_researchers

                if r.get("institution") == session.get("institution")

            ]



        # System Admin -> all researchers

        else:

            researchers = all_researchers




    # ================= GET PUBLICATIONS =================


    response = requests.get(
        f"{API_URL}/publications/",
        headers=headers
    )


    if response.status_code == 200:


        all_publications = response.json()



        # Researcher -> only own publications

        if session["role"] == "researcher":


            publications = [

                p for p in all_publications

                if p.get("researcher_id") in 
                [r["id"] for r in researchers]

            ]



        # Institution Admin -> publications of institution researchers

        elif session["role"] == "institution_admin":


            institution_researcher_ids = [

                r["id"]

                for r in researchers

            ]


            publications = [

                p for p in all_publications

                if p.get("researcher_id") 
                in institution_researcher_ids

            ]



        # System Admin -> all publications

        else:


            publications = all_publications




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
        "Authorization": f"Bearer " + session["token"]
    }



    # -------- Get Conferences --------

    if session["role"] in ["researcher", "institution_admin"]:

        response = requests.get(
            f"{API_URL}/conferences/my",
            headers=headers
        )


    else:

        # System Admin sees all conferences

        response = requests.get(
            f"{API_URL}/conferences/",
            headers=headers
        )



    conferences = []


    if response.status_code == 200:

        conferences = response.json()



    # -------- Convert Conference Date --------

    for conference in conferences:

        try:

            conference["conference_date_obj"] = datetime.strptime(
                conference["conference_date"],
                "%Y-%m-%d"
            )

        except:

            conference["conference_date_obj"] = None





    # -------- Get Institutions for Dropdown --------

    response = requests.get(
        f"{API_URL}/institutions/",
        headers=headers
    )


    institutions = []


    if response.status_code == 200:

        institutions = response.json()




    return render_template(
        "conferences.html",
        conferences=conferences,
        institutions=institutions,
        today=datetime.today()
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

        "website": request.form.get("website"),

        "institution": request.form.get("institution"),

        "event_type": request.form.get("event_type")

    }


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    response = requests.post(
        f"{API_URL}/conferences/",
        json=data,
        headers=headers
    )


    print("ADD CONFERENCE:", response.status_code)
    print(response.text)


    return redirect(url_for("conferences"))

# ---------------------- Edit Conference ----------------------

# ---------------------- Edit Conference ----------------------

@app.route("/conference/edit/<int:id>", methods=["GET","POST"])
def edit_conference(id):

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }



    # -------- UPDATE CONFERENCE --------

    if request.method == "POST":


        data = {

            "title": request.form.get("title"),

            "location": request.form.get("location"),

            "conference_date": request.form.get("conference_date"),

            "website": request.form.get("website")

        }
        print("JSON SENT TO FASTAPI:")
        print(data)


        response = requests.put(

            f"{API_URL}/conferences/{id}",

            json=data,

            headers=headers

        )


        print("UPDATE CONFERENCE STATUS:", response.status_code)
        print("UPDATE RESPONSE:", response.text)



        return redirect(
            url_for("conferences")
        )




    # -------- GET CONFERENCE DETAILS --------

    response = requests.get(

        f"{API_URL}/conferences/{id}",

        headers=headers

    )


    conference = response.json()


    return render_template(

        "edit_conference.html",

        conference=conference

    )
# ---------------------- Delete Conference ----------------------

@app.route("/conference/delete/<int:id>")
def delete_conference(id):

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    response = requests.delete(
        f"{API_URL}/conferences/{id}",
        headers=headers
    )


    print("DELETE CONFERENCE:", response.status_code)


    return redirect(url_for("conferences"))

@app.route("/conference/register/<int:id>", methods=["GET", "POST"])
def register_conference(id):

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    # Get conference details

    response = requests.get(
        f"{API_URL}/conferences/{id}",
        headers=headers
    )


    if response.status_code != 200:
        return "Conference not found"


    conference = response.json()



    # Get publications for presenter selection

    publications_response = requests.get(
        f"{API_URL}/publications/user/{session['user_id']}",
        headers=headers
    )


    publications = []

    if publications_response.status_code == 200:
        publications = publications_response.json()



    if request.method == "POST":


        data = {

            "conference_id": id,

            "participation_type": request.form["participation_type"],

            "presentation_title": request.form.get("presentation_title"),

            "publication_id": request.form.get("publication_id") or None,

            "presentation_mode": request.form.get("presentation_mode")

        }



        response = requests.post(

            f"{API_URL}/conference-registration/",

            json=data,

            headers=headers

        )


        if response.status_code == 200:

            return redirect(
                url_for("conferences")
            )



    return render_template(

        "register_conference.html",

        conference=conference,

        publications=publications

    )

@app.route("/conference/<int:id>/participants")
def conference_participants(id):

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    response = requests.get(
        f"{API_URL}/conference-registration/conference/{id}",
        headers=headers
    )


    participants = []


    if response.status_code == 200:

        participants = response.json()

        print("PARTICIPANTS DATA:")
        print(participants)


    else:

        print("ERROR:", response.status_code)
        print(response.text)



    return render_template(
        "conference_participants.html",
        participants=participants
    )

@app.route("/my-conference-history")
def my_conference_history():

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    response = requests.get(
        f"{API_URL}/conference-registration/my",
        headers=headers
    )


    registrations = []


    if response.status_code == 200:
        registrations = response.json()


    return render_template(
        "my_conference_history.html",
        registrations=registrations
    )
    
@app.route("/institutions")
def institutions():

    if "token" not in session:
        return redirect(url_for("login"))

    headers = {
        "Authorization": f"Bearer {session['token']}"
    }

    response = requests.get(
        f"{API_URL}/institutions/",
        headers=headers
    )

    institutions = []

    if response.status_code == 200:
        institutions = response.json()

    return render_template(
        "institutions.html",
        institutions=institutions
    )

@app.route("/institutions/edit/<int:id>", methods=["GET", "POST"])
def edit_institution(id):

    if "token" not in session:
        return redirect(url_for("login"))

    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    if request.method == "POST":

        data = {
            "website": request.form["website"],
            "phone": request.form["phone"]
        }


        response = requests.put(
            f"{API_URL}/institutions/{id}",
            json=data,
            headers=headers
        )


        if response.status_code == 200:
            return redirect(url_for("institutions"))



    response = requests.get(
        f"{API_URL}/institutions/{id}",
        headers=headers
    )


    institution = response.json()


    return render_template(
        "edit_institution.html",
        institution=institution
    )

@app.route("/institutions/delete/<int:id>")
def delete_institution(id):

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    response = requests.delete(
        f"{API_URL}/institutions/{id}",
        headers=headers
    )


    if response.status_code == 200:
        return redirect(url_for("institutions"))


    else:
        print("DELETE INSTITUTION ERROR:")
        print(response.text)

        return "Failed to delete institution"
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