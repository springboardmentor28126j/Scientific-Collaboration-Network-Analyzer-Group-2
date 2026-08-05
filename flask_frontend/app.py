from flask import Flask, render_template, request, redirect, url_for, session
import requests
from datetime import datetime
from flask import send_file
from io import BytesIO
from reportlab.pdfgen import canvas
import openpyxl

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


                # Researcher details
                session["researcher_id"] = data.get(
                    "researcher_id"
                )


                # Institution details
                session["institution"] = data.get(
                    "institution"
                )

                session["institution_id"] = data.get(
                    "institution_id"
                )


                print("LOGIN USER:", data["email"])

                print("LOGIN ROLE:", data["role"])

                print(
                    "INSTITUTION:",
                    data.get("institution")
                )

                print(
                    "INSTITUTION ID:",
                    data.get("institution_id")
                )


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

    # Get all institutions for dropdown
    institutions = []

    try:
        response = requests.get(f"{API_URL}/institutions/public")

        if response.status_code == 200:
            institutions = response.json()

    except:
        pass


    if request.method == "POST":

        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        role = request.form.get("role")

        institution_id = request.form.get("institution_id")


        if password != confirm_password:

            return render_template(
                "register.html",
                institutions=institutions,
                error="Passwords do not match"
            )


        try:

            # Prepare registration data
            data = {

                "full_name": full_name,
                "email": email,
                "password": password,
                "role": role

            }


            # Add institution only if selected
            if institution_id:

                data["institution_id"] = int(institution_id)



            response = requests.post(

                f"{API_URL}/register",

                json=data

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

                institutions=institutions,

                error=error_message

            )



        except requests.exceptions.ConnectionError:

            return render_template(

                "register.html",

                institutions=institutions,

                error="Backend server is not running."

            )



    return render_template(

        "register.html",

        institutions=institutions

    )

# ---------------------- Dashboard ----------------------
@app.route("/dashboard")
def dashboard():

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    user_count = 0
    researcher_count = 0
    publication_count = 0
    institution_count = 0
    project_count = 0
    collaboration_count = 0
    department_count = 0
    conference_count = 0

    activities = []



    # ================= COMMON DATA =================


    # Users

    response = requests.get(
        f"{API_URL}/users",
        headers=headers
    )

    if response.status_code == 200:

        users = response.json()
        user_count = len(users)



    # Institutions

    response = requests.get(
        f"{API_URL}/institutions/",
        headers=headers
    )

    if response.status_code == 200:

        institutions = response.json()
        institution_count = len(institutions)



    # Projects

    response = requests.get(
        f"{API_URL}/projects/",
        headers=headers
    )

    projects = []

    if response.status_code == 200:

        projects = response.json()



    # Project Members  ✅ ADDED

    response = requests.get(
        f"{API_URL}/project-members/",
        headers=headers
    )

    project_members = []

    if response.status_code == 200:

        project_members = response.json()



    # Institution Collaborations

    response = requests.get(
        f"{API_URL}/institution-collaborations/",
        headers=headers
    )

    collaborations = []

    if response.status_code == 200:

        collaborations = response.json()



    project_collaboration_ids = [

        c.get("project_id")

        for c in collaborations

    ]



    # Activities

    response = requests.get(
        f"{API_URL}/activities/",
        headers=headers
    )

    if response.status_code == 200:

        activities = response.json()





    # ================= INSTITUTION ADMIN =================


    if session["role"] == "institution_admin":


        response = requests.get(
            f"{API_URL}/researchers/",
            headers=headers
        )


        researchers = []


        if response.status_code == 200:

            researchers = response.json()


            researchers = [

                r for r in researchers

                if r.get("institution")
                == session.get("institution")

            ]


            researcher_count = len(researchers)



        response = requests.get(
            f"{API_URL}/publications/",
            headers=headers
        )


        if response.status_code == 200:


            publications = response.json()


            researcher_ids = [

                r["id"]

                for r in researchers

            ]


            publications = [

                p for p in publications

                if p.get("researcher_id")
                in researcher_ids

            ]


            publication_count = len(publications)



        departments = set()


        for r in researchers:

            if r.get("department"):

                departments.add(
                    r.get("department")
                )


        department_count = len(departments)



        response = requests.get(
            f"{API_URL}/conferences/",
            headers=headers
        )


        if response.status_code == 200:

            conferences = response.json()


            conferences = [

                c for c in conferences

                if c.get("institution")
                == session.get("institution")

            ]


            conference_count = len(conferences)



        institution_projects = [

            p for p in projects

            if p.get("institution_id")
            == session.get("institution_id")

        ]


        project_count = len(institution_projects)



        collaborative_projects = []


        for project in institution_projects:


            if (
                project.get("team_members_count",0)>0
                or
                project.get("id") in project_collaboration_ids
            ):

                collaborative_projects.append(project)



        collaboration_count = len(
            collaborative_projects
        )






    # ================= RESEARCHER =================


    elif session["role"] == "researcher":

        print("SESSION DATA:", session)
        print("PROJECT MEMBERS:", project_members)
        response = requests.get(
            f"{API_URL}/publications/user/{session['user_id']}",
            headers=headers
        )


        if response.status_code == 200:

            publications = response.json()
            publication_count = len(publications)

            # Researcher Conferences

            response = requests.get(
               f"{API_URL}/conference-registration/my",
               headers=headers
            )


            if response.status_code == 200:

                researcher_conferences = response.json()

                conference_count = len(
                    researcher_conferences
                )

        # ✅ UPDATED PROJECT FILTERING


        my_project_ids = [

            pm.get("project_id")

            for pm in project_members

            if pm.get("researcher_id")
            == session.get("researcher_id")

        ]



        researcher_projects = [

            p for p in projects

            if p.get("id")
            in my_project_ids

        ]



        project_count = len(
            researcher_projects
        )





        # ✅ UPDATED COLLABORATION CHECK


        collaborative_projects = []


        for project in researcher_projects:


            project_id = project.get("id")


            has_team_members = any(

                pm.get("project_id")
                == project_id

                for pm in project_members

            )


            has_institution_collaboration = (

                project_id
                in project_collaboration_ids

            )



            if (
                has_team_members
                or
                has_institution_collaboration
            ):

                collaborative_projects.append(project)



        collaboration_count = len(
            collaborative_projects
        )






    # ================= SYSTEM ADMIN =================


    elif session["role"] == "system_admin":


        response = requests.get(
            f"{API_URL}/researchers/",
            headers=headers
        )


        if response.status_code == 200:

            researchers = response.json()
            researcher_count = len(researchers)




        response = requests.get(
            f"{API_URL}/publications/",
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




        project_count = len(projects)



        collaborative_projects = []


        for project in projects:


            if (
                project.get("team_members_count",0)>0
                or
                project.get("id") in project_collaboration_ids
            ):

                collaborative_projects.append(project)



        collaboration_count = len(
            collaborative_projects
        )





    return render_template(

        "dashboard.html",

        role=session["role"],

        name=session["full_name"],

        user_count=user_count,

        researcher_count=researcher_count,

        publication_count=publication_count,

        institution_count=institution_count,

        project_count=project_count,

        collaboration_count=collaboration_count,

        department_count=department_count,

        conference_count=conference_count,

        activities=activities

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


    print("TOKEN:", session.get("token"))
    print("HEADERS:", headers)
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
            print("UPDATE PROFILE STATUS:", response.status_code)
            print("UPDATE PROFILE RESPONSE:", response.text)

        else:

            # Profile doesn't exist -> Create
            response = requests.post(

                f"{API_URL}/researchers/profile",

                json=data,

                headers=headers

            )

        if response.status_code == 200:

           # Refresh researcher id after profile save/update
            profile_response = requests.get(
               f"{API_URL}/researchers/profile/me",
               headers=headers
            )

            if profile_response.status_code == 200:

                researcher_data = profile_response.json()

                session["researcher_id"] = researcher_data.get("id")

                print(
                    "UPDATED SESSION RESEARCHER ID:",
                     session["researcher_id"]
                )

            return redirect(
                 url_for("researcher_profile")
            )

        try:
            error_message = response.json().get("detail")
        except Exception:
              error_message = response.text


        return render_template(
                "profile.html",
                 error=error_message
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

    researcher_id = session.get("researcher_id")

    print("SESSION RESEARCHER ID:", researcher_id)

    if not researcher_id:
         return "Researcher ID is missing in session!", 400


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


    print("INSTITUTION STATUS:", response.status_code)
    print("INSTITUTION DATA:", response.text)


    institutions = []


    if response.status_code == 200:
        institutions = response.json()


    return render_template(
        "institutions.html",
        institutions=institutions
    )
# ---------------------- Add Institution ----------------------

@app.route("/institutions/add", methods=["POST"])
def add_institution():

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    data = {

        "name": request.form.get("name"),

        "institution_type": request.form.get("institution_type"),

        "location": request.form.get("location"),

        "website": request.form.get("website"),

        "phone": request.form.get("phone")

    }


    response = requests.post(

        f"{API_URL}/institutions/",

        json=data,

        headers=headers

    )


    print("ADD INSTITUTION STATUS:", response.status_code)
    print("ADD INSTITUTION RESPONSE:", response.text)



    if response.status_code == 200:

        return redirect(
            url_for("institutions")
        )



    # if error, return same institutions page

    institutions_response = requests.get(
        f"{API_URL}/institutions/",
        headers=headers
    )


    institutions = []

    if institutions_response.status_code == 200:
        institutions = institutions_response.json()



    return render_template(

        "institutions.html",

        institutions=institutions,

        error=response.text

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
            "institution_type": request.form["institution_type"],
            "location": request.form["location"],
            "website": request.form["website"],
            "phone": request.form["phone"]
        }


        response = requests.put(
            f"{API_URL}/institutions/{id}",
            json=data,
            headers=headers
        )


        print("UPDATE DATA:", data)
        print("UPDATE RESPONSE:", response.text)


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

# ==========================
# Projects
# ==========================

# ==========================
# Projects
# ==========================

@app.route("/projects")
def projects():

    if "token" not in session:
        return redirect(url_for("login"))

    headers = {
        "Authorization": f"Bearer {session['token']}"
    }

    role = session.get("role")

    # ==========================
    # System Admin
    # ==========================

    if role == "system_admin":

        project_response = requests.get(
            f"{API_URL}/projects/",
            headers=headers
        )

    # ==========================
    # Institution Admin
    # ==========================

    elif role == "institution_admin":

        institution_id = session.get("institution_id")

        project_response = requests.get(
            f"{API_URL}/projects/institution/{institution_id}",
            headers=headers
        )

    # ==========================
    # Researcher
    # ==========================

    elif role == "researcher":

        return render_template(
            "projects.html",
            projects=[],
            institutions=[]
        )

    else:

        return "Unauthorized"

    projects = project_response.json()
    # ==========================
    # Get Institutions
    # ==========================

    institution_response = requests.get(
        f"{API_URL}/institutions/",
        headers=headers
    )

    institutions = institution_response.json()

    return render_template(
        "projects.html",
        projects=projects,
        institutions=institutions
    )
# ==========================
# Add Project
# ==========================

@app.route("/projects/add", methods=["POST"])
def add_project():

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    data = {

        "project_name": request.form["project_name"],

        "description": request.form["description"],

        "start_date": request.form["start_date"],

        "end_date": request.form.get("end_date") or None,

        "status": request.form["status"],

        "institution_id": int(request.form["institution_id"])

    }


    response = requests.post(
        f"{API_URL}/projects/",
        json=data,
        headers=headers
    )


    if response.status_code == 200:
       return redirect(url_for("projects"))


    print("PROJECT ERROR:", response.status_code)
    print(response.text)

    return response.text

@app.route("/projects/edit/<int:id>", methods=["GET", "POST"])
def edit_project(id):

    if "token" not in session:
        return redirect(url_for("login"))

    headers = {
        "Authorization": f"Bearer {session['token']}"
    }

    # Get project details
    project_response = requests.get(
        f"{API_URL}/projects/{id}",
        headers=headers
    )

    if project_response.status_code != 200:
        return "Project not found"

    project = project_response.json()

    # Get institutions for dropdown
    institution_response = requests.get(
        f"{API_URL}/institutions/",
        headers=headers
    )

    institutions = institution_response.json()

    if request.method == "POST":

        data = {

            "project_name": request.form["project_name"],

            "description": request.form["description"],

            "start_date": request.form["start_date"],

            "end_date": request.form["end_date"] or None,

            "status": request.form["status"],

            "institution_id": int(request.form["institution_id"])

        }

        response = requests.put(
            f"{API_URL}/projects/{id}",
            json=data,
            headers=headers
        )

        if response.status_code == 200:
            return redirect(url_for("projects"))

        return "Error updating project"

    return render_template(
        "edit_project.html",
        project=project,
        institutions=institutions
    )
@app.route("/projects/delete/<int:id>")
def delete_project(id):

    if "token" not in session:
        return redirect(url_for("login"))

    headers = {
        "Authorization": f"Bearer {session['token']}"
    }

    response = requests.delete(
        f"{API_URL}/projects/{id}",
        headers=headers
    )

    if response.status_code == 200:
        return redirect(url_for("projects"))

    return "Error deleting project"

# ==========================
# Collaboration
# ==========================

@app.route("/collaboration")
def collaboration():

    if "token" not in session:
        return redirect(url_for("login"))

    headers = {
        "Authorization": f"Bearer {session['token']}"
    }

    role = session.get("role")


    # ==========================
    # Get Projects
    # ==========================

    if role == "system_admin":

        response = requests.get(
            f"{API_URL}/projects/",
            headers=headers
        )


    elif role == "institution_admin":

        institution_id = session.get("institution_id")

        response = requests.get(
            f"{API_URL}/projects/institution/{institution_id}",
            headers=headers
        )


    else:

        return "Unauthorized"



    projects = response.json()



    # ==========================
    # Get All Collaborations
    # ==========================

    collab_response = requests.get(
        f"{API_URL}/institution-collaborations/",
        headers=headers
    )


    if collab_response.status_code == 200:

        all_collaborations = collab_response.json()
        print("ALL COLLABORATIONS:", all_collaborations)
    else:

        all_collaborations = []



    # ==========================
    # Add Counts
    # ==========================

    for project in projects:


        # -------- Team Count --------

        member_response = requests.get(
            f"{API_URL}/project-members/project/{project['id']}",
            headers=headers
        )


        if member_response.status_code == 200:

            members = member_response.json()

            project["team_count"] = len(members)

        else:

            project["team_count"] = 0



        project["collaboration_count"] = len(
          [
             c for c in all_collaborations
             if c.get("project_id") == project.get("id")
          ]
        )



        print(
            project["project_name"],
            "TEAM:",
            project["team_count"],
            "COLLAB:",
            project["collaboration_count"]
        )



    return render_template(
        "collaboration.html",
        projects=projects
    )
@app.route("/collaboration/project/<int:project_id>")
def manage_team(project_id):

    if "token" not in session:
        return redirect(url_for("login"))

    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    # ==========================
    # Get Project Details
    # ==========================

    project_response = requests.get(
        f"{API_URL}/projects/{project_id}",
        headers=headers
    )

    if project_response.status_code != 200:
        return "Project not found"


    project = project_response.json()



    # ==========================
    # Get All Researchers
    # ==========================

    researcher_response = requests.get(
        f"{API_URL}/researchers/",
        headers=headers
    )


    if researcher_response.status_code == 200:

        all_researchers = researcher_response.json()

    else:

        all_researchers = []



    # ==========================
    # Get Main Institution Name
    # ==========================

    project_institution = project.get("institution")


    # If project has only institution_id
    if not project_institution and project.get("institution_id"):


        institution_response = requests.get(
            f"{API_URL}/institutions/{project.get('institution_id')}",
            headers=headers
        )


        if institution_response.status_code == 200:

            project_institution = institution_response.json().get("name")



    # ==========================
    # Main Institution Researchers
    # ==========================

    researchers = [

        r for r in all_researchers

        if r.get("institution") == project_institution

    ]



    # ==========================
    # Add Collaborated Institution Researchers
    # ==========================


    collab_response = requests.get(
        f"{API_URL}/institution-collaborations/",
        headers=headers
    )


    if collab_response.status_code == 200:

        collaborations = collab_response.json()

    else:

        collaborations = []



    for collab in collaborations:


        if collab.get("project_id") == project_id:


            collaborating_institution_id = collab.get(
                "collaborating_institution_id"
            )


            institution_response = requests.get(
                f"{API_URL}/institutions/{collaborating_institution_id}",
                headers=headers
            )


            if institution_response.status_code == 200:


                collaborating_institution = institution_response.json()


                institution_name = collaborating_institution.get(
                    "name"
                )


                extra_researchers = [

                    r for r in all_researchers

                    if r.get("institution") == institution_name

                ]


                researchers.extend(
                    extra_researchers
                )



    # ==========================
    # Remove Duplicate Researchers
    # ==========================

    unique_researchers = {}


    for r in researchers:

        unique_researchers[r["id"]] = r



    researchers = list(
        unique_researchers.values()
    )



    # ==========================
    # Get Assigned Team Members
    # ==========================


    member_response = requests.get(
        f"{API_URL}/project-members/project/{project_id}",
        headers=headers
    )


    if member_response.status_code == 200:

        members = member_response.json()

    else:

        members = []



    # ==========================
    # Remove Already Assigned Researchers
    # ==========================

    assigned_ids = [

        member["researcher_id"]

        for member in members

    ]



    available_researchers = [

        researcher

        for researcher in researchers

        if researcher["id"] not in assigned_ids

    ]



    print("PROJECT:", project)

    print("MAIN INSTITUTION:", project_institution)

    print("ALL RESEARCHERS:", all_researchers)

    print("AVAILABLE RESEARCHERS:", available_researchers)



    return render_template(
        "manage_team.html",
        project=project,
        researchers=available_researchers,
        members=members
    )
# ==========================
# Assign Team Member
# ==========================

@app.route("/collaboration/project/<int:project_id>/assign", methods=["POST"])
def assign_member(project_id):

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    data = {

        "project_id": project_id,

        "researcher_id": request.form.get("researcher_id"),

        "role": request.form.get("role")

    }


    response = requests.post(
        f"{API_URL}/project-members/",
        json=data,
        headers=headers
    )


    print("ASSIGN MEMBER STATUS:", response.status_code)
    print("ASSIGN MEMBER RESPONSE:", response.text)



    return redirect(
        url_for(
            "manage_team",
            project_id=project_id
        )
    )
# ==========================
# Remove Team Member
# ==========================

@app.route("/collaboration/member/<int:member_id>/remove")
def remove_member(member_id):

    if "token" not in session:
        return redirect(url_for("login"))

    headers = {
        "Authorization": f"Bearer {session['token']}"
    }

    response = requests.delete(
        f"{API_URL}/project-members/{member_id}",
        headers=headers
    )

    return redirect(request.referrer or url_for("collaboration"))
@app.route("/institution-collaborations")
def institution_collaborations():

    token = session.get("token")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(
        "http://127.0.0.1:8000/institution-collaborations/",
        headers=headers
    )

    collaborations = response.json()

    return render_template(
        "institution_collaborations.html",
        collaborations=collaborations
    )
@app.route("/add-collaboration/<int:project_id>", methods=["POST"])
def add_collaboration(project_id):

    token = session.get("token")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    institution_id = request.form.get("institution_id")


    data = {
        "project_id": project_id,
        "collaborating_institution_id": int(institution_id)
    }


    response = requests.post(
        f"{API_URL}/institution-collaborations/",
        json=data,
        headers=headers
    )


    print("ADD COLLAB STATUS:", response.status_code)
    print("ADD COLLAB RESPONSE:", response.text)


    return redirect(
        url_for(
            "manage_collaboration",
            project_id=project_id
        )
    )
@app.route("/manage-collaboration/<int:project_id>")
def manage_collaboration(project_id):

    if "token" not in session:
        return redirect(url_for("login"))


    token = session.get("token")

    headers = {
        "Authorization": f"Bearer {token}"
    }


    # ==========================
    # Get Selected Project
    # ==========================

    project_response = requests.get(
        f"{API_URL}/projects/{project_id}",
        headers=headers
    )


    if project_response.status_code == 200:

        project = project_response.json()

    else:

        print("PROJECT ERROR:")
        print(project_response.status_code)
        print(project_response.text)

        return "Project not found"



    # ==========================
    # Get Institutions
    # ==========================

    institution_response = requests.get(
        f"{API_URL}/institutions/",
        headers=headers
    )


    if institution_response.status_code == 200:

        institutions = institution_response.json()

    else:

        print("INSTITUTION ERROR:")
        print(institution_response.status_code)
        print(institution_response.text)

        institutions = []



    # ==========================
    # Get Existing Collaborations
    # ==========================

    collaboration_response = requests.get(
        f"{API_URL}/institution-collaborations/",
        headers=headers
    )


    print(
        "COLLAB STATUS:",
        collaboration_response.status_code
    )

    print(
        "COLLAB RESPONSE:",
        collaboration_response.text
    )


    if collaboration_response.status_code == 200:

        collaborations = collaboration_response.json()

    else:

        collaborations = []



    # ==========================
    # Filter Project Collaborations
    # ==========================

    project_collaborations = []


    for item in collaborations:

        if item.get("project_name") == project.get("project_name"):

            project_collaborations.append(item)



    print("PROJECT:", project)

    print(
        "ALL COLLABORATIONS:",
        collaborations
    )

    print(
        "FILTERED COLLABORATIONS:",
        project_collaborations
    )



    return render_template(
        "manage_collaboration.html",
        project=project,
        institutions=institutions,
        collaborations=project_collaborations
    )
@app.route("/my-collaborations")
def my_collaborations():

    # Check Login
    if "token" not in session:
        return redirect(url_for("login"))


    researcher_id = session.get("researcher_id")


    if not researcher_id:
        return redirect(url_for("dashboard"))



    headers = {
        "Authorization": f"Bearer {session['token']}"
    }



    response = requests.get(
        f"{API_URL}/projects/researcher/{researcher_id}",
        headers=headers
    )



    if response.status_code == 200:

        projects = response.json()

    else:

        projects = []



    return render_template(
        "my_collaborations.html",
        collaborations=projects
    )
@app.route("/citation-reference")
def citation_reference():

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }



    # ================= GET CITATIONS =================

    citation_response = requests.get(
        f"{API_URL}/citations/",
        headers=headers
    )

    citations = []

    if citation_response.status_code == 200:
        citations = citation_response.json()



    # ================= GET REFERENCES =================

    reference_response = requests.get(
        f"{API_URL}/references/",
        headers=headers
    )

    references = []

    if reference_response.status_code == 200:
        references = reference_response.json()



    # ================= GET PUBLICATIONS =================

    publication_response = requests.get(
        f"{API_URL}/publications/",
        headers=headers
    )

    all_publications = []

    if publication_response.status_code == 200:
        all_publications = publication_response.json()



    # ================= GET RESEARCHERS =================

    researcher_response = requests.get(
        f"{API_URL}/researchers/",
        headers=headers
    )

    researchers = []

    if researcher_response.status_code == 200:
        researchers = researcher_response.json()



    role = session.get("role")



    # =====================================================
    # ROLE BASED PUBLICATION ACCESS
    # =====================================================


    if role == "researcher":


        citing_publications = [

            p for p in all_publications

            if p.get("researcher_id")
            == session.get("researcher_id")

        ]



    elif role == "institution_admin":


        institution_name = session.get("institution")


        institution_researcher_ids = [

            r.get("id")

            for r in researchers

            if r.get("institution")
            == institution_name

        ]


        citing_publications = [

            p for p in all_publications

            if p.get("researcher_id")
            in institution_researcher_ids

        ]



    elif role == "system_admin":


        citing_publications = all_publications



    else:

        citing_publications = []



    # =====================================================
    # FILTER CITATION & REFERENCE RECORDS
    # =====================================================


    allowed_publication_ids = [

        p.get("id")

        for p in citing_publications

    ]



    citations = [

        c for c in citations

        if c.get("publication_id")
        in allowed_publication_ids

    ]



    references = [

        r for r in references

        if r.get("publication_id")
        in allowed_publication_ids

    ]



    # =====================================================
    # ADD PUBLICATION TITLES FOR TABLE DISPLAY
    # =====================================================


    publication_map = {

        p.get("id"): p

        for p in all_publications

    }



    # Citation table data

    for citation in citations:


        citing_pub = publication_map.get(
            citation.get("publication_id")
        )


        cited_pub = publication_map.get(
            citation.get("cited_publication_id")
        )


        citation["publication_title"] = (

            citing_pub.get("title")
            if citing_pub
            else "Unknown"

        )


        citation["cited_publication_title"] = (

            cited_pub.get("title")
            if cited_pub
            else "Unknown"

        )



    # Reference table data

    for reference in references:


        publication = publication_map.get(
            reference.get("publication_id")
        )


        reference["publication_title"] = (

            publication.get("title")
            if publication
            else "Unknown"

        )



    # =====================================================
    # DROPDOWN DATA
    # =====================================================


    cited_publications = [

        p for p in all_publications

        if p.get("status") == "Published"

    ]


    reference_publications = citing_publications



    # =====================================================
    # SEND TO HTML
    # =====================================================


    return render_template(

        "citation_reference.html",

        citations=citations,

        references=references,


        publications=citing_publications,

        cited_publications=cited_publications,

        reference_publications=reference_publications,


        citation_count=len(citations),

        reference_count=len(references)

    )
@app.route("/add-citation", methods=["POST"])
def add_citation():

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    data = {

        "publication_id": int(request.form["publication_id"]),

        "cited_publication_id": int(request.form["cited_publication_id"])

    }


    response = requests.post(
        "http://127.0.0.1:8000/citations/",
        json=data,
        headers=headers
    )


    if response.status_code in [200, 201]:
        return redirect(url_for("citation_reference"))


    else:
        print("STATUS:", response.status_code)
        print("ERROR:", response.text)
        return redirect(url_for("citation_reference"))
@app.route("/delete-citation/<int:citation_id>")
def delete_citation(citation_id):

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    response = requests.delete(
           f"http://127.0.0.1:8000/citations/{citation_id}",
           headers=headers
    )


    return redirect(url_for("citation_reference"))

@app.route("/add-reference", methods=["POST"])
def add_reference():

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    data = {

        "publication_id": int(request.form["publication_id"]),

        "reference_title": request.form["reference_title"],

        "author": request.form["author"],

        "publication_year": int(request.form["publication_year"]),

        "doi": request.form["doi"]

    }


    response = requests.post(
        "http://127.0.0.1:8000/references/",
        json=data,
        headers=headers
    )


    if response.status_code in [200, 201]:
        return redirect(url_for("citation_reference"))


    else:
        print(response.text)
        return redirect(url_for("citation_reference"))

@app.route("/delete-reference/<int:reference_id>")
def delete_reference(reference_id):

    if "token" not in session:
        return redirect(url_for("login"))

    headers = {
        "Authorization": f"Bearer {session['token']}"
    }

    response = requests.delete(
        f"http://127.0.0.1:8000/references/{reference_id}",
        headers=headers
    )

    return redirect(url_for("citation_reference"))

# ---------------------- Reports ----------------------

@app.route("/reports")
def reports():

    if "token" not in session:
        return redirect(url_for("login"))

    role = session.get("role")

    if role not in [
        "system_admin",
        "institution_admin"
    ]:
        return "Unauthorized Access", 403


    return render_template(
        "reports.html"
    )



@app.route("/publication-report")
def publication_report():

    if "token" not in session:
        return redirect(url_for("login"))

    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    params = {}

    if session.get("role") == "institution_admin":

        params["institution_id"] = session.get("institution_id")


    response = requests.get(
        f"{API_URL}/reports/publication-report",
        headers=headers,
        params=params
    )

    print("REPORT STATUS:", response.status_code)
    print("REPORT RESPONSE:", response.text)
    publication_data = response.json()


    return render_template(

        "publication_report.html",

        publication_report=publication_data.get("table", []),

        publication_chart=publication_data.get("chart", [])

    )





@app.route("/research-report")
def research_report():

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    params = {}

    if session.get("role") == "institution_admin":

        params["institution_id"] = session.get("institution_id")


    response = requests.get(

        f"{API_URL}/reports/research-report",

        headers=headers,

        params=params

    )


    research_data = response.json()


    return render_template(

        "research_report.html",

        research_report=research_data.get("table", []),

        research_chart=research_data.get("chart", [])

    )





@app.route("/collaboration-report")
def collaboration_report():

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {

        "Authorization": f"Bearer {session['token']}"

    }


    params = {}

    if session.get("role") == "institution_admin":

        params["institution_id"] = session.get("institution_id")


    response = requests.get(

        f"{API_URL}/reports/collaboration-report",

        headers=headers,

        params=params

    )


    collaboration_data = response.json()


    return render_template(

        "collaboration_report.html",

        collaboration_report=collaboration_data.get("table", []),

        collaboration_chart=collaboration_data.get("chart", [])

    )





@app.route("/institution-report")
def institution_report():

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {

        "Authorization": f"Bearer {session['token']}"

    }


    params = {}

    if session.get("role") == "institution_admin":

        params["institution_id"] = session.get("institution_id")


    response = requests.get(

        f"{API_URL}/reports/institution-report",

        headers=headers,

        params=params

    )


    institution_data = response.json()


    return render_template(

        "institution_report.html",

        institution_report=institution_data.get("table", []),

        institution_chart=institution_data.get("chart", [])

    )
# ---------------- Research Report Export ----------------


@app.route("/research-report/pdf")
def research_report_pdf():

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    response = requests.get(
        f"{API_URL}/reports/research-report/pdf",
        headers=headers
    )


    if response.status_code == 200:

        return send_file(
            BytesIO(response.content),
            download_name="research_report.pdf",
            as_attachment=True
        )


    return "PDF Export Failed", 400





@app.route("/research-report/excel")
def research_report_excel():

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    response = requests.get(
        f"{API_URL}/reports/research-report/excel",
        headers=headers
    )


    if response.status_code == 200:

        return send_file(
            BytesIO(response.content),
            download_name="research_report.xlsx",
            as_attachment=True
        )


    return "Excel Export Failed", 400

# ---------------- Publication Report Export ----------------


@app.route("/publication-report/pdf")
def publication_report_pdf():

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    response = requests.get(
        f"{API_URL}/reports/publication-report/pdf",
        headers=headers
    )


    if response.status_code == 200:

        return send_file(
            BytesIO(response.content),
            download_name="publication_report.pdf",
            as_attachment=True
        )


    return "PDF Export Failed", 400





@app.route("/publication-report/excel")
def publication_report_excel():

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    response = requests.get(
        f"{API_URL}/reports/publication-report/excel",
        headers=headers
    )


    if response.status_code == 200:

        return send_file(
            BytesIO(response.content),
            download_name="publication_report.xlsx",
            as_attachment=True
        )


    return "Excel Export Failed", 400

# ---------------- Collaboration Report Export ----------------


@app.route("/collaboration-report/pdf")
def collaboration_report_pdf():

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    response = requests.get(
        f"{API_URL}/reports/collaboration-report/pdf",
        headers=headers
    )


    if response.status_code == 200:

        return send_file(
            BytesIO(response.content),
            download_name="collaboration_report.pdf",
            as_attachment=True
        )


    return "PDF Export Failed", 400





@app.route("/collaboration-report/excel")
def collaboration_report_excel():

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    response = requests.get(
        f"{API_URL}/reports/collaboration-report/excel",
        headers=headers
    )


    if response.status_code == 200:

        return send_file(
            BytesIO(response.content),
            download_name="collaboration_report.xlsx",
            as_attachment=True
        )


    return "Excel Export Failed", 400

# ---------------- Institution Report Export ----------------


@app.route("/institution-report/pdf")
def institution_report_pdf():

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    response = requests.get(
        f"{API_URL}/reports/institution-report/pdf",
        headers=headers
    )


    if response.status_code == 200:

        return send_file(
            BytesIO(response.content),
            download_name="institution_report.pdf",
            as_attachment=True
        )


    return "PDF Export Failed", 400





@app.route("/institution-report/excel")
def institution_report_excel():

    if "token" not in session:
        return redirect(url_for("login"))


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    response = requests.get(
        f"{API_URL}/reports/institution-report/excel",
        headers=headers
    )


    if response.status_code == 200:

        return send_file(
            BytesIO(response.content),
            download_name="institution_report.xlsx",
            as_attachment=True
        )


    return "Excel Export Failed", 400
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