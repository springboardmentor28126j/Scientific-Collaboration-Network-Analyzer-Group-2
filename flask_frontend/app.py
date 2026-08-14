from flask import Flask, render_template, request, redirect, url_for, session,flash
import requests
from datetime import datetime
from flask import send_file
from io import BytesIO
from reportlab.pdfgen import canvas
import openpyxl
from flask import jsonify

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

    # Reviewer dashboard counts
    pending_review_count = 0
    reviewed_paper_count = 0

    activities = []

    # =========================================
    # COMMON DATA
    # =========================================

    # -----------------------------------------
    # Users
    # -----------------------------------------

    response = requests.get(
        f"{API_URL}/users",
        headers=headers
    )

    if response.status_code == 200:

        users = response.json()

        if isinstance(users, list):
            user_count = len(users)

    # -----------------------------------------
    # Institutions
    # -----------------------------------------

    response = requests.get(
        f"{API_URL}/institutions/",
        headers=headers
    )

    if response.status_code == 200:

        institutions = response.json()

        if isinstance(institutions, list):
            institution_count = len(institutions)

    # -----------------------------------------
    # Projects
    # -----------------------------------------

    response = requests.get(
        f"{API_URL}/projects/",
        headers=headers
    )

    projects = []

    if response.status_code == 200:

        response_data = response.json()

        if isinstance(response_data, dict):

            projects = response_data.get(
                "data",
                []
            )

        else:

            projects = response_data

        if not isinstance(projects, list):
            projects = []

    # -----------------------------------------
    # Project Members
    # -----------------------------------------

    response = requests.get(
        f"{API_URL}/project-members/",
        headers=headers
    )

    project_members = []

    if response.status_code == 200:

        project_members = response.json()

        if not isinstance(project_members, list):
            project_members = []

    # -----------------------------------------
    # Institution Collaborations
    # -----------------------------------------

    response = requests.get(
        f"{API_URL}/institution-collaborations/",
        headers=headers
    )

    collaborations = []

    if response.status_code == 200:

        collaborations = response.json()

        if not isinstance(collaborations, list):
            collaborations = []

    project_collaboration_ids = [
        c.get("project_id")
        for c in collaborations
        if isinstance(c, dict)
    ]

    # =========================================
    # ROLE
    # =========================================

    role = session.get("role")

    # =========================================
    # INSTITUTION ADMIN
    # =========================================

    if role == "institution_admin":

        # -------------------------------------
        # Researchers
        # -------------------------------------

        response = requests.get(
            f"{API_URL}/researchers/",
            headers=headers
        )

        researchers = []

        if response.status_code == 200:

            response_data = response.json()

            if isinstance(response_data, dict):

                researchers = response_data.get(
                    "data",
                    []
                )

            else:

                researchers = response_data

            if not isinstance(researchers, list):
                researchers = []

            researchers = [
                r
                for r in researchers
                if (
                    isinstance(r, dict)
                    and r.get("institution")
                    == session.get("institution")
                )
            ]

            researcher_count = len(researchers)

        # -------------------------------------
        # Publications
        # -------------------------------------

        response = requests.get(
            f"{API_URL}/publications/",
            headers=headers
        )

        if response.status_code == 200:

            response_data = response.json()

            if isinstance(response_data, dict):

                publications = response_data.get(
                    "data",
                    []
                )

            else:

                publications = response_data

            if not isinstance(publications, list):
                publications = []

            researcher_ids = [
                r.get("id")
                for r in researchers
                if isinstance(r, dict)
            ]

            publications = [
                p
                for p in publications
                if (
                    isinstance(p, dict)
                    and p.get("researcher_id")
                    in researcher_ids
                )
            ]

            publication_count = len(publications)

        # -------------------------------------
        # Departments
        # -------------------------------------

        departments = set()

        for researcher in researchers:

            if (
                isinstance(researcher, dict)
                and researcher.get("department")
            ):

                departments.add(
                    researcher.get("department")
                )

        department_count = len(departments)

        # -------------------------------------
        # Conferences
        # -------------------------------------

        response = requests.get(
            f"{API_URL}/conferences/",
            headers=headers
        )

        if response.status_code == 200:

            response_data = response.json()

            if isinstance(response_data, dict):

                conferences = response_data.get(
                    "data",
                    []
                )

            else:

                conferences = response_data

            if not isinstance(conferences, list):
                conferences = []

            conferences = [
                c
                for c in conferences
                if (
                    isinstance(c, dict)
                    and c.get("institution")
                    == session.get("institution")
                )
            ]

            conference_count = len(conferences)

        # -------------------------------------
        # Institution Projects
        # -------------------------------------

        institution_projects = [
            p
            for p in projects
            if (
                isinstance(p, dict)
                and p.get("institution_id")
                == session.get("institution_id")
            )
        ]

        project_count = len(institution_projects)

        # -------------------------------------
        # Collaborations
        # -------------------------------------

        collaborative_projects = []

        for project in institution_projects:

            if (
                project.get("team_members_count", 0) > 0
                or project.get("id")
                in project_collaboration_ids
            ):

                collaborative_projects.append(
                    project
                )

        collaboration_count = len(
            collaborative_projects
        )

    # =========================================
    # RESEARCHER
    # =========================================

    elif role == "researcher":

        # -------------------------------------
        # My Publications
        # -------------------------------------

        response = requests.get(
            f"{API_URL}/publications/user/{session['user_id']}",
            headers=headers
        )

        if response.status_code == 200:

            publications = response.json()

            if isinstance(publications, list):

                publication_count = len(
                    publications
                )

        # -------------------------------------
        # My Conferences
        # -------------------------------------

        response = requests.get(
            f"{API_URL}/conference-registration/my",
            headers=headers
        )

        if response.status_code == 200:

            researcher_conferences = response.json()

            if isinstance(
                researcher_conferences,
                list
            ):

                conference_count = len(
                    researcher_conferences
                )

        # -------------------------------------
        # My Projects
        # -------------------------------------

        my_project_ids = [
            pm.get("project_id")
            for pm in project_members
            if (
                isinstance(pm, dict)
                and pm.get("researcher_id")
                == session.get("researcher_id")
            )
        ]

        researcher_projects = [
            p
            for p in projects
            if (
                isinstance(p, dict)
                and p.get("id")
                in my_project_ids
            )
        ]

        project_count = len(
            researcher_projects
        )

        # -------------------------------------
        # My Collaborations
        # -------------------------------------

        collaborative_projects = []

        for project in researcher_projects:

            project_id = project.get("id")

            has_team_members = any(
                pm.get("project_id") == project_id
                for pm in project_members
                if isinstance(pm, dict)
            )

            has_institution_collaboration = (
                project_id
                in project_collaboration_ids
            )

            if (
                has_team_members
                or has_institution_collaboration
            ):

                collaborative_projects.append(
                    project
                )

        collaboration_count = len(
            collaborative_projects
        )

    # =========================================
    # REVIEWER
    # =========================================

    elif role == "reviewer":

        response = requests.get(
            f"{API_URL}/reviewer/my-reviews",
            headers=headers
        )

        reviews = []

        if response.status_code == 200:

            reviews = response.json()

            if not isinstance(reviews, list):
                reviews = []

        # -------------------------------------
        # Pending Reviews
        # -------------------------------------

        pending_reviews = [
            review
            for review in reviews
            if (
                isinstance(review, dict)
                and review.get("decision")
                == "Pending"
            )
        ]

        # -------------------------------------
        # Completed Reviews
        # -------------------------------------

        reviewed_reviews = [
            review
            for review in reviews
            if (
                isinstance(review, dict)
                and review.get("decision")
                in [
                    "Approved",
                    "Rejected",
                    "Needs Revision"
                ]
            )
        ]

        pending_review_count = len(
            pending_reviews
        )

        reviewed_paper_count = len(
            reviewed_reviews
        )

    # =========================================
    # SYSTEM ADMIN
    # =========================================

    elif role == "system_admin":

        # -------------------------------------
        # Researchers
        # -------------------------------------

        response = requests.get(
            f"{API_URL}/researchers/",
            headers=headers
        )

        if response.status_code == 200:

            response_data = response.json()

            if isinstance(response_data, dict):

                researchers = response_data.get(
                    "data",
                    []
                )

            else:

                researchers = response_data

            if isinstance(researchers, list):

                researcher_count = len(
                    researchers
                )

        # -------------------------------------
        # Publications
        # -------------------------------------

        response = requests.get(
            f"{API_URL}/publications/",
            headers=headers
        )

        if response.status_code == 200:

            response_data = response.json()

            if isinstance(response_data, dict):

                publications = response_data.get(
                    "data",
                    []
                )

            else:

                publications = response_data

            if isinstance(publications, list):

                publication_count = len(
                    publications
                )

        # -------------------------------------
        # Conferences
        # -------------------------------------

        response = requests.get(
            f"{API_URL}/conferences/",
            headers=headers
        )

        if response.status_code == 200:

            response_data = response.json()

            if isinstance(response_data, dict):

                conferences = response_data.get(
                    "data",
                    []
                )

            else:

                conferences = response_data

            if isinstance(conferences, list):

                conference_count = len(
                    conferences
                )

        # -------------------------------------
        # Projects
        # -------------------------------------

        project_count = len(projects)

        # -------------------------------------
        # Collaborations
        # -------------------------------------

        collaborative_projects = []

        for project in projects:

            if (
                project.get("team_members_count", 0) > 0
                or project.get("id")
                in project_collaboration_ids
            ):

                collaborative_projects.append(
                    project
                )

        collaboration_count = len(
            collaborative_projects
        )

    # =========================================
    # RECENT ACTIVITIES
    # =========================================

    response = requests.get(
        f"{API_URL}/activities/",
        headers=headers
    )

    print(
        "ACTIVITY API STATUS:",
        response.status_code
    )

    print(
        "ACTIVITY API RESPONSE:",
        response.text
    )

    activities = []

    if response.status_code == 200:

        try:

            activities = response.json()

        except ValueError:

            print(
                "ACTIVITY API returned invalid JSON"
            )

            activities = []

        if not isinstance(activities, list):

            print(
                "ACTIVITY API response is not a list"
            )

            activities = []

    else:

        print(
            "Activity API Error:",
            response.status_code,
            response.text
        )

    # -----------------------------------------
    # Latest activities first
    # -----------------------------------------

    activities = sorted(
        activities,
        key=lambda activity: (
            activity.get("created_at", "")
            if isinstance(activity, dict)
            else ""
        ),
        reverse=True
    )

    # -----------------------------------------
    # Dashboard displays latest 5
    # -----------------------------------------

    activities = activities[:5]

    print(
        "FINAL DASHBOARD ACTIVITIES:",
        activities
    )

    # =========================================
    # RETURN DASHBOARD
    # =========================================

    return render_template(
        "dashboard.html",

        role=role,
        name=session["full_name"],

        user_count=user_count,
        researcher_count=researcher_count,
        publication_count=publication_count,
        institution_count=institution_count,
        project_count=project_count,
        collaboration_count=collaboration_count,
        department_count=department_count,
        conference_count=conference_count,

        pending_review_count=pending_review_count,
        reviewed_paper_count=reviewed_paper_count,

        activities=activities
    )
# ---------------------- Researchers ----------------------

# ==========================
# Researchers
# ==========================

@app.route("/researchers")
def researchers():

    if "token" not in session:
        return redirect(url_for("login"))

    headers = {
        "Authorization": f"Bearer {session['token']}"
    }

    role = session.get("role")

    page = request.args.get(
        "page",
        1,
        type=int
    )

    page_size = request.args.get(
        "page_size",
        5,
        type=int
    )

    sort_by = request.args.get(
        "sort_by",
        "full_name"
    )

    order = request.args.get(
        "order",
        "asc"
    )

    # Safety
    if page < 1:
        page = 1

    if page_size < 1 or page_size > 100:
        page_size = 5

    if sort_by not in [
        "full_name",
        "email",
        "institution"
    ]:
        sort_by = "full_name"

    if order not in [
        "asc",
        "desc"
    ]:
        order = "asc"

    # ==================================================
    # GET RESEARCHERS
    # ==================================================

    response = requests.get(
        f"{API_URL}/researchers/",
        headers=headers,
        params={
            "page": page,
            "page_size": page_size,
            "sort_by": sort_by,
            "order": order
        }
    )

    print(
        "GET RESEARCHERS:",
        response.status_code,
        response.text
    )

    researchers = []
    pagination = {
        "page": page,
        "page_size": page_size,
        "total_records": 0,
        "total_pages": 1,
        "offset": 0
    }

    if response.status_code == 200:

        data = response.json()

        researchers = data.get(
            "data",
            []
        )

        pagination = data.get(
            "pagination",
            pagination
        )

    else:

        try:
            error = response.json().get(
                "detail",
                "Failed to load researchers"
            )
        except Exception:
            error = "Failed to load researchers"

        return render_template(
            "researchers.html",
            researchers=[],
            pagination=pagination,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            order=order,
            error=error
        )

    return render_template(
        "researchers.html",
        researchers=researchers,
        pagination=pagination,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        order=order
    )
# ---------------------- Add Researcher ----------------------

@app.route("/researchers/add", methods=["POST"])
def add_researcher():

    if "token" not in session:
        return redirect(url_for("login"))

    role = session.get("role")

    # Only these roles can add
    if role not in [
        "institution_admin",
        "system_admin"
    ]:
        return redirect(
            url_for("researchers")
        )

    data = {
        "full_name": request.form.get("full_name"),
        "email": request.form.get("email"),
        "department": request.form.get("department"),
        "institution": request.form.get("institution"),
        "designation": request.form.get("designation"),
        "research_interests": request.form.get(
            "research_interests"
        ),
        "skills": request.form.get("skills"),
        "phone": request.form.get("phone")
    }

    # Institution Admin must use their institution
    if role == "institution_admin":

        data["institution"] = session.get(
            "institution"
        )

    headers = {
        "Authorization": f"Bearer {session['token']}"
    }

    response = requests.post(
        f"{API_URL}/researchers/",
        json=data,
        headers=headers
    )

    print(
        "ADD RESEARCHER STATUS:",
        response.status_code
    )

    print(
        "ADD RESEARCHER RESPONSE:",
        response.text
    )

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
        researchers=[],
        pagination={
            "page": 1,
            "page_size": 5,
            "total_records": 0,
            "total_pages": 1,
            "offset": 0
        },
        page=1,
        page_size=5,
        sort_by="full_name",
        order="asc",
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

    # ==================================================
    # LOGIN CHECK
    # ==================================================

    if "token" not in session:
        return redirect(url_for("login"))

    headers = {
        "Authorization": f"Bearer {session['token']}"
    }

    publications = []
    researchers = []

    # ==================================================
    # PAGINATION + SORTING PARAMETERS
    # ==================================================

    page = request.args.get(
        "page",
        1,
        type=int
    )

    page_size = request.args.get(
        "page_size",
        10,
        type=int
    )

    sort_by = request.args.get(
        "sort_by",
        "year"
    )

    order = request.args.get(
        "order",
        "desc"
    )

    # ==================================================
    # SAFE VALUES
    # ==================================================

    if page < 1:
        page = 1

    if page_size < 1 or page_size > 100:
        page_size = 10

    if sort_by not in [
        "year",
        "title"
    ]:
        sort_by = "year"

    if order not in [
        "asc",
        "desc"
    ]:
        order = "desc"

    # ==================================================
    # GET RESEARCHERS
    # ==================================================

    researcher_response = requests.get(

        f"{API_URL}/researchers/",

        headers=headers,

        params={

            "page": 1,

            "page_size": 1000,

            "sort_by": "full_name",

            "order": "asc"

        }

    )

    if researcher_response.status_code == 200:

        researcher_data = (
            researcher_response.json()
        )

        # FastAPI response:
        #
        # {
        #     "data": [...],
        #     "pagination": {...}
        # }

        if isinstance(
            researcher_data,
            dict
        ):

            all_researchers = (
                researcher_data.get(
                    "data",
                    []
                )
            )

        else:

            all_researchers = (
                researcher_data
            )

        # Only dictionary records

        all_researchers = [

            r

            for r in all_researchers

            if isinstance(
                r,
                dict
            )

        ]

        # ==================================================
        # RESEARCHER ROLE
        # ==================================================

        if session["role"] == "researcher":

            researchers = [

                r

                for r in all_researchers

                if r.get("user_id")
                == session.get("user_id")

            ]

        # ==================================================
        # INSTITUTION ADMIN
        # ==================================================

        elif session["role"] == "institution_admin":

            institution_name = (
                session.get("institution")
            )

            researchers = [

                r

                for r in all_researchers

                if r.get("institution")
                == institution_name

            ]

        # ==================================================
        # SYSTEM ADMIN / OTHER
        # ==================================================

        else:

            researchers = (
                all_researchers
            )

    # ==================================================
    # GET ALL PUBLICATIONS
    # ==================================================

    publication_response = requests.get(

        f"{API_URL}/publications/",

        headers=headers,

        params={

            # IMPORTANT:
            # Ask FastAPI for all records.
            # FastAPI now allows up to 1000.

            "page": 1,

            "page_size": 1000,

            "sort_by": "year",

            "order": "desc"

        }

    )

    # ==================================================
    # PUBLICATION RESPONSE
    # ==================================================

    if publication_response.status_code == 200:

        publication_data = (
            publication_response.json()
        )

        if isinstance(
            publication_data,
            dict
        ):

            all_publications = (
                publication_data.get(
                    "data",
                    []
                )
            )

        else:

            all_publications = (
                publication_data
            )

        # Only dictionary records

        all_publications = [

            p

            for p in all_publications

            if isinstance(
                p,
                dict
            )

        ]

        # ==================================================
        # GET RESEARCHER IDS
        # ==================================================

        researcher_ids = [

            r.get("id")

            for r in researchers

            if isinstance(
                r,
                dict
            )

            and r.get("id") is not None

        ]

        # ==================================================
        # ROLE-BASED FILTERING
        # ==================================================

        if session["role"] in [

            "researcher",

            "institution_admin"

        ]:

            publications = [

                p

                for p in all_publications

                if p.get("researcher_id")
                in researcher_ids

            ]

        else:

            publications = (
                all_publications
            )

    else:

        # ==================================================
        # API ERROR
        # ==================================================

        print(
            "PUBLICATION API ERROR:",
            publication_response.status_code
        )

        print(
            "PUBLICATION API RESPONSE:",
            publication_response.text
        )

        publications = []

    # ==================================================
    # SORTING
    # ==================================================

    if sort_by == "title":

        publications.sort(

            key=lambda p: (
                p.get("title") or ""
            ).casefold(),

            reverse=(
                order == "desc"
            )

        )

    else:

        publications.sort(

            key=lambda p: (
                p.get(
                    "publication_year",
                    0
                )
                or 0
            ),

            reverse=(
                order == "desc"
            )

        )

    # ==================================================
    # PAGINATION
    # ==================================================

    total_records = len(
        publications
    )

    total_pages = (

        (
            total_records
            + page_size
            - 1
        )
        // page_size

        if total_records > 0

        else 1

    )

    # ==================================================
    # PREVENT INVALID PAGE
    # ==================================================

    if page > total_pages:

        page = total_pages

    if page < 1:

        page = 1

    # ==================================================
    # SLICE RECORDS
    # ==================================================

    start = (
        (page - 1)
        * page_size
    )

    end = (
        start
        + page_size
    )

    paginated_publications = (
        publications[start:end]
    )

    # ==================================================
    # PAGINATION INFORMATION
    # ==================================================

    pagination = {

        "page": page,

        "page_size": page_size,

        "total_records":
            total_records,

        "total_pages":
            total_pages,

        "offset":
            start

    }

    # ==================================================
    # SEND TO TEMPLATE
    # ==================================================

    return render_template(

        "publications.html",

        publications=paginated_publications,

        researchers=researchers,

        pagination=pagination,

        sort_by=sort_by,

        order=order,

        page_size=page_size

    )

@app.route("/publication/add", methods=["POST"])
def add_publication():

    if "token" not in session:
        return redirect(url_for("login"))

    print("FORM DATA:", request.form)
    print("Session:", session)

    # Researcher selected in the form
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

@app.route("/publication-recommend")
def publication_recommend():

    if "token" not in session:
        return {"error": "Not authenticated"}, 401

    headers = {
        "Authorization": f"Bearer {session['token']}"
    }

    query = request.args.get("query", "").strip()

    if not query:
        return {"error": "Query is required"}, 400

    response = requests.get(
        f"{API_URL}/publications/recommend",
        params={
            "q": query
        },
        headers=headers
    )

    print(
        "RECOMMENDATION API:",
        response.status_code,
        response.text
    )

    if response.status_code != 200:
        return {
            "error": "Unable to get recommendations"
        }, response.status_code

    data = response.json()

    return jsonify(
        data.get("recommendations", [])
    )
# ---------------------- Conferences ----------------------

@app.route("/conferences")
def conferences():

    if "token" not in session:
        return redirect(url_for("login"))

    headers = {
        "Authorization": f"Bearer {session['token']}"
    }

    # ==================================================
    # PAGINATION / SORTING
    # ==================================================

    conference_page = request.args.get(
        "conference_page",
        1,
        type=int
    )

    conference_page_size = request.args.get(
        "conference_page_size",
        5,
        type=int
    )

    conference_sort_by = request.args.get(
        "conference_sort_by",
        "title"
    )

    conference_order = request.args.get(
        "conference_order",
        "desc"
    )

    # Keep values safe
    if conference_page < 1:
        conference_page = 1

    if conference_page_size not in [5, 10, 20]:
        conference_page_size = 5

    if conference_sort_by not in [
        "title",
        "organizer",
        "institution",
        "event_type",
        "location",
        "conference_date"
    ]:
        conference_sort_by = "title"

    if conference_order not in ["asc", "desc"]:
        conference_order = "desc"

    # ==================================================
    # GET CONFERENCES
    # ==================================================

    if session["role"] in [
        "researcher",
        "institution_admin"
    ]:

        response = requests.get(
            f"{API_URL}/conferences/my",
            headers=headers
        )

    else:

        response = requests.get(
            f"{API_URL}/conferences/",
            headers=headers
        )

    conferences = []

    if response.status_code == 200:

        conference_data = response.json()

        if isinstance(conference_data, dict):

            conferences = conference_data.get(
                "data",
                []
            )

        elif isinstance(conference_data, list):

            conferences = conference_data

    # ==================================================
    # SORT CONFERENCES
    # ==================================================

    reverse_order = conference_order == "desc"

    if conference_sort_by == "title":

        conferences.sort(
            key=lambda x: (
                x.get("title") or ""
            ).lower(),
            reverse=reverse_order
        )

    elif conference_sort_by == "organizer":

        conferences.sort(
            key=lambda x: (
                x.get("organizer") or ""
            ).lower(),
            reverse=reverse_order
        )

    elif conference_sort_by == "institution":

        conferences.sort(
            key=lambda x: (
                x.get("institution") or ""
            ).lower(),
            reverse=reverse_order
        )

    elif conference_sort_by == "event_type":

        conferences.sort(
            key=lambda x: (
                x.get("event_type") or ""
            ).lower(),
            reverse=reverse_order
        )

    elif conference_sort_by == "location":

        conferences.sort(
            key=lambda x: (
                x.get("location") or ""
            ).lower(),
            reverse=reverse_order
        )

    elif conference_sort_by == "conference_date":

        conferences.sort(
            key=lambda x: (
                x.get("conference_date") or ""
            ),
            reverse=reverse_order
        )

    # ==================================================
    # TOTAL RECORDS
    # ==================================================

    total_records = len(conferences)

    total_pages = (
        (total_records + conference_page_size - 1)
        // conference_page_size
    )

    # ==================================================
    # MAKE SURE PAGE IS VALID
    # ==================================================

    if total_pages > 0 and conference_page > total_pages:

        conference_page = total_pages

    if conference_page < 1:

        conference_page = 1

    # ==================================================
    # PAGINATION
    # ==================================================

    offset = (
        (conference_page - 1)
        * conference_page_size
    )

    paginated_conferences = conferences[
        offset:
        offset + conference_page_size
    ]

    # ==================================================
    # CONVERT CONFERENCE DATE
    # ==================================================

    for conference in paginated_conferences:

        try:

            conference["conference_date_obj"] = (
                datetime.strptime(
                    conference["conference_date"],
                    "%Y-%m-%d"
                )
            )

        except:

            conference["conference_date_obj"] = None

    # ==================================================
    # CHECK RESEARCHER REGISTERED CONFERENCES
    # ==================================================

    registered_conferences = []

    if session["role"] == "researcher":

        reg_response = requests.get(
            f"{API_URL}/conference-registration/my",
            headers=headers
        )

        if reg_response.status_code == 200:

            registrations = reg_response.json()

            for reg in registrations:

                registered_conferences.append(
                    reg["conference_id"]
                )

    # ==================================================
    # ADD REGISTERED FLAG
    # ==================================================

    for conference in paginated_conferences:

        if conference["id"] in registered_conferences:

            conference["registered"] = True

        else:

            conference["registered"] = False

    # ==================================================
    # GET INSTITUTIONS
    # ==================================================

    institution_response = requests.get(
        f"{API_URL}/institutions/",
        headers=headers
    )

    institutions = []

    if institution_response.status_code == 200:

        institution_data = institution_response.json()

        if isinstance(institution_data, dict):

            institutions = institution_data.get(
                "data",
                []
            )

        elif isinstance(institution_data, list):

            institutions = institution_data

    # ==================================================
    # PAGINATION DATA
    # ==================================================

    pagination = {

        "page": conference_page,

        "page_size": conference_page_size,

        "total_records": total_records,

        "total_pages": total_pages,

        "offset": offset

    }

    # ==================================================
    # RENDER
    # ==================================================

    return render_template(

        "conferences.html",

        conferences=paginated_conferences,

        institutions=institutions,

        today=datetime.today(),

        conference_pagination=pagination,

        conference_page=conference_page,

        conference_page_size=conference_page_size,

        conference_sort_by=conference_sort_by,

        conference_order=conference_order

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
# ==========================
# Institutions
# ==========================

@app.route("/institutions")
def institutions():

    if "token" not in session:
        return redirect(url_for("login"))

    headers = {
        "Authorization": f"Bearer {session['token']}"
    }

    # ==========================
    # Pagination / Sorting
    # ==========================

    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 5, type=int)
    sort_by = request.args.get("sort_by", "name")
    order = request.args.get("order", "asc")

    params = {
        "page": page,
        "page_size": page_size,
        "sort_by": sort_by,
        "order": order
    }

    # ==========================
    # Get Institutions
    # ==========================

    response = requests.get(
        f"{API_URL}/institutions/",
        headers=headers,
        params=params
    )

    print("INSTITUTION STATUS:", response.status_code)
    print("INSTITUTION DATA:", response.text)

    institutions = []
    pagination = {}

    if response.status_code == 200:

        institution_data = response.json()

        if isinstance(institution_data, dict):

            institutions = institution_data.get("data", [])

            pagination = institution_data.get(
                "pagination",
                {}
            )

        else:

            institutions = institution_data
            pagination = {}

    return render_template(
        "institutions.html",
        institutions=institutions,
        pagination=pagination,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        order=order
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


@app.route("/projects")
def projects():

    if "token" not in session:
        return redirect(url_for("login"))

    headers = {
        "Authorization": f"Bearer {session['token']}"
    }

    role = session.get("role")

    # ==========================
    # Pagination / Sorting
    # ==========================

    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 5, type=int)
    sort_by = request.args.get("sort_by", "start_date")
    order = request.args.get("order", "desc")

    params = {
        "page": page,
        "page_size": page_size,
        "sort_by": sort_by,
        "order": order
    }

    # ==========================
    # System Admin
    # ==========================

    if role == "system_admin":

        project_response = requests.get(
            f"{API_URL}/projects/",
            headers=headers,
            params=params
        )

    # ==========================
    # Institution Admin
    # ==========================

    elif role == "institution_admin":

        institution_id = session.get("institution_id")

        project_response = requests.get(
            f"{API_URL}/projects/institution/{institution_id}",
            headers=headers,
            params=params
        )

    # ==========================
    # Researcher
    # ==========================

    elif role == "researcher":

        return render_template(
            "projects.html",
            projects=[],
            institutions=[],
            pagination={}
        )

    else:
        return "Unauthorized"

    # ==========================
    # Projects Response
    # ==========================

    project_data = project_response.json()

    if isinstance(project_data, dict):

        projects = project_data.get("data", [])
        pagination = project_data.get("pagination", {})

    else:

        projects = project_data
        pagination = {}

    # ==========================
    # Get Institutions
    # ==========================

    institution_response = requests.get(
        f"{API_URL}/institutions/",
        headers=headers
    )

    institution_data = institution_response.json()

    if isinstance(institution_data, dict):
        institutions = institution_data.get("data", [])
    else:
        institutions = institution_data

    return render_template(
        "projects.html",
        projects=projects,
        institutions=institutions,
        pagination=pagination,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        order=order
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

    # ==================================================
    # PAGINATION / SORTING
    # ==================================================

    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 5, type=int)
    sort_by = request.args.get("sort_by", "project_name")
    order = request.args.get("order", "asc")

    # Keep values safe
    if page < 1:
        page = 1

    if page_size not in [5, 10, 20]:
        page_size = 5

    if sort_by not in ["project_name", "status"]:
        sort_by = "project_name"

    if order not in ["asc", "desc"]:
        order = "asc"

    params = {
        "page": page,
        "page_size": page_size,
        "sort_by": sort_by,
        "order": order
    }

    # ==================================================
    # GET PROJECTS
    # ==================================================

    if role == "system_admin":

        response = requests.get(
            f"{API_URL}/projects/",
            headers=headers,
            params=params
        )

    elif role == "institution_admin":

        institution_id = session.get("institution_id")

        response = requests.get(
            f"{API_URL}/projects/institution/{institution_id}",
            headers=headers,
            params=params
        )

    else:

        return "Unauthorized"

    # ==================================================
    # PROJECT RESPONSE
    # ==================================================

    projects = []
    backend_pagination = {}

    if response.status_code == 200:

        project_data = response.json()

        if isinstance(project_data, dict):

            projects = project_data.get(
                "data",
                []
            )

            backend_pagination = project_data.get(
                "pagination",
                {}
            )

        elif isinstance(project_data, list):

            projects = project_data

    # ==================================================
    # NORMALIZE PAGINATION
    # ==================================================

    total_records = backend_pagination.get(
        "total_records",
        len(projects)
    )

    total_pages = backend_pagination.get(
        "total_pages",
        1
    )

    backend_page = backend_pagination.get(
        "page",
        page
    )

    backend_page_size = backend_pagination.get(
        "page_size",
        page_size
    )

    # Calculate offset ourselves if backend doesn't provide it
    offset = backend_pagination.get(
        "offset",
        (backend_page - 1) * backend_page_size
    )

    pagination = {

        "page": backend_page,

        "page_size": backend_page_size,

        "total_records": total_records,

        "total_pages": total_pages,

        "offset": offset

    }

    # ==================================================
    # GET ALL COLLABORATIONS
    # ==================================================

    collab_response = requests.get(
        f"{API_URL}/institution-collaborations/",
        headers=headers
    )

    all_collaborations = []

    if collab_response.status_code == 200:

        collaboration_data = collab_response.json()

        if isinstance(collaboration_data, dict):

            all_collaborations = collaboration_data.get(
                "data",
                []
            )

        elif isinstance(collaboration_data, list):

            all_collaborations = collaboration_data

    # ==================================================
    # ADD COUNTS
    # ==================================================

    for project in projects:

        # ----------------------------------------------
        # Team Count
        # ----------------------------------------------

        member_response = requests.get(
            f"{API_URL}/project-members/project/{project['id']}",
            headers=headers
        )

        if member_response.status_code == 200:

            members_data = member_response.json()

            if isinstance(members_data, dict):

                members = members_data.get(
                    "data",
                    []
                )

            elif isinstance(members_data, list):

                members = members_data

            else:

                members = []

            project["team_count"] = len(members)

        else:

            project["team_count"] = 0

        # ----------------------------------------------
        # Collaboration Count
        # ----------------------------------------------

        project["collaboration_count"] = len(
            [
                c
                for c in all_collaborations
                if isinstance(c, dict)
                and c.get("project_id")
                == project.get("id")
            ]
        )

    # ==================================================
    # RENDER
    # ==================================================

    return render_template(

        "collaboration.html",

        projects=projects,

        pagination=pagination,

        page=page,

        page_size=page_size,

        sort_by=sort_by,

        order=order

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

    # =====================================================
    # PAGINATION / SORTING
    # =====================================================

    citation_page = request.args.get(
        "citation_page", 1, type=int
    )

    citation_page_size = request.args.get(
        "citation_page_size", 5, type=int
    )

    citation_sort_by = request.args.get(
        "citation_sort_by", "publication_title"
    )

    citation_order = request.args.get(
        "citation_order", "desc"
    )

    reference_page = request.args.get(
        "reference_page", 1, type=int
    )

    reference_page_size = request.args.get(
        "reference_page_size", 5, type=int
    )

    reference_sort_by = request.args.get(
        "reference_sort_by", "publication_title"
    )

    reference_order = request.args.get(
        "reference_order", "desc"
    )

    role = session.get("role")

    # =====================================================
    # GET PUBLICATIONS
    # =====================================================

    publication_response = requests.get(
        f"{API_URL}/publications/",
        headers=headers
    )

    all_publications = []

    if publication_response.status_code == 200:

        publication_data = publication_response.json()

        if isinstance(publication_data, dict):

            all_publications = publication_data.get(
                "data", []
            )

        else:

            all_publications = publication_data

    # =====================================================
    # GET RESEARCHERS
    # =====================================================

    researcher_response = requests.get(
        f"{API_URL}/researchers/",
        headers=headers
    )

    researchers = []

    if researcher_response.status_code == 200:

        researcher_data = researcher_response.json()

        if isinstance(researcher_data, dict):

            researchers = researcher_data.get(
                "data", []
            )

        else:

            researchers = researcher_data

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
    # ALLOWED PUBLICATION IDS
    # =====================================================

    allowed_publication_ids = [

        p.get("id")

        for p in citing_publications

    ]

    # =====================================================
    # PUBLICATION MAP
    # =====================================================

    publication_map = {

        p.get("id"): p

        for p in all_publications

    }

    # =====================================================
    # GET ALL CITATIONS
    # =====================================================

    citation_params = {
        "page": 1,
        "page_size": 10000
    }

    citation_response = requests.get(
        f"{API_URL}/citations/",
        headers=headers,
        params=citation_params
    )

    all_citations = []

    if citation_response.status_code == 200:

        citation_data = citation_response.json()

        if isinstance(citation_data, dict):

            all_citations = citation_data.get(
                "data", []
            )

        else:

            all_citations = citation_data

    # =====================================================
    # FILTER CITATIONS BY ROLE
    # =====================================================

    all_citations = [

        c for c in all_citations

        if c.get("publication_id")
        in allowed_publication_ids

    ]

    # =====================================================
    # CITATION SORTING
    # =====================================================

    if citation_sort_by == "publication_title":

        all_citations.sort(

            key=lambda c:
            publication_map.get(
                c.get("publication_id"), {}
            ).get("title", "").lower(),

            reverse=(citation_order == "desc")

        )

    elif citation_sort_by == "cited_publication_title":

        all_citations.sort(

            key=lambda c:
            publication_map.get(
                c.get("cited_publication_id"), {}
            ).get("title", "").lower(),

            reverse=(citation_order == "desc")

        )

    # =====================================================
    # CITATION PAGINATION
    # =====================================================

    citation_total_records = len(all_citations)

    citation_total_pages = (

        (
            citation_total_records
            + citation_page_size
            - 1
        )
        // citation_page_size

        if citation_total_records > 0

        else 0

    )

    citation_offset = (

        (citation_page - 1)
        * citation_page_size

    )

    citations = all_citations[

        citation_offset:
        citation_offset + citation_page_size

    ]

    citation_pagination = {

        "page": citation_page,

        "page_size": citation_page_size,

        "total_records": citation_total_records,

        "total_pages": citation_total_pages,

        "offset": citation_offset

    }

    # =====================================================
    # GET ALL REFERENCES
    # =====================================================

    reference_params = {
        "page": 1,
        "page_size": 10000
    }

    reference_response = requests.get(
        f"{API_URL}/references/",
        headers=headers,
        params=reference_params
    )

    all_references = []

    if reference_response.status_code == 200:

        reference_data = reference_response.json()

        if isinstance(reference_data, dict):

            all_references = reference_data.get(
                "data", []
            )

        else:

            all_references = reference_data

    # =====================================================
    # FILTER REFERENCES BY ROLE
    # =====================================================

    all_references = [

        r for r in all_references

        if r.get("publication_id")
        in allowed_publication_ids

    ]

    # =====================================================
    # REFERENCE SORTING
    # =====================================================

    if reference_sort_by == "publication_title":

        all_references.sort(

            key=lambda r:
            publication_map.get(
                r.get("publication_id"), {}
            ).get("title", "").lower(),

            reverse=(reference_order == "desc")

        )

    elif reference_sort_by == "reference_title":

        all_references.sort(

            key=lambda r:
            r.get("reference_title", "").lower(),

            reverse=(reference_order == "desc")

        )

    elif reference_sort_by == "publication_year":

        all_references.sort(

            key=lambda r:
            r.get("publication_year") or 0,

            reverse=(reference_order == "desc")

        )

    # =====================================================
    # REFERENCE PAGINATION
    # =====================================================

    reference_total_records = len(all_references)

    reference_total_pages = (

        (
            reference_total_records
            + reference_page_size
            - 1
        )
        // reference_page_size

        if reference_total_records > 0

        else 0

    )

    reference_offset = (

        (reference_page - 1)
        * reference_page_size

    )

    references = all_references[

        reference_offset:
        reference_offset + reference_page_size

    ]

    reference_pagination = {

        "page": reference_page,

        "page_size": reference_page_size,

        "total_records": reference_total_records,

        "total_pages": reference_total_pages,

        "offset": reference_offset

    }

    # =====================================================
    # CITATION TABLE DATA
    # =====================================================

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

    # =====================================================
    # REFERENCE TABLE DATA
    # =====================================================

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

        # TOTAL COUNTS
        citation_count=citation_total_records,
        reference_count=reference_total_records,

        # PAGINATION
        citation_pagination=citation_pagination,
        reference_pagination=reference_pagination,

        # CITATION CONTROLS
        citation_page=citation_page,
        citation_page_size=citation_page_size,
        citation_sort_by=citation_sort_by,
        citation_order=citation_order,

        # REFERENCE CONTROLS
        reference_page=reference_page,
        reference_page_size=reference_page_size,
        reference_sort_by=reference_sort_by,
        reference_order=reference_order

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

        "cited_publication_id": int(
            request.form["cited_publication_id"]
        )

    }


    response = requests.post(

        f"{API_URL}/citations/",

        json=data,

        headers=headers

    )


    if response.status_code in [200,201]:

        flash(
            "Citation added successfully",
            "success"
        )

        return redirect(
            url_for("citation_reference")
        )


    else:

        try:

            error_message = response.json().get(
                "detail",
                "Unable to add citation"
            )

        except:

            error_message = "Unable to add citation"



        print("CITATION ERROR:", error_message)


        flash(
            error_message,
            "error"
        )


        return redirect(
            url_for("citation_reference")
        )
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

@app.route("/notifications")
def notifications():

    if "token" not in session:
        return redirect(url_for("login"))


    user_id = session.get("user_id")

    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    response = requests.get(
        f"http://127.0.0.1:8000/notifications/{user_id}",
        headers=headers
    )


    if response.status_code == 200:
        notifications = response.json()

    else:
        notifications = []


    return render_template(
        "notifications.html",
        notifications=notifications
    )
@app.route("/notification-count")
def notification_count():

    if "token" not in session:
        return {"count": 0}


    user_id = session.get("user_id")


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    response = requests.get(
        f"http://127.0.0.1:8000/notifications/unread-count/{user_id}",
        headers=headers
    )


    if response.status_code == 200:
        return response.json()


    return {"count":0}
@app.route("/notifications-data")
def notifications_data():

    if "token" not in session:
        return []


    user_id = session.get("user_id")


    headers = {
        "Authorization": f"Bearer {session['token']}"
    }


    response = requests.get(
        f"{API_URL}/notifications/{user_id}",
        headers=headers
    )


    if response.status_code == 200:
        return response.json()


    return []

# ==========================
# Reviewer - My Reviews
# ==========================

@app.route("/reviewer")
def reviewer():

    if "token" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "reviewer":
        return redirect(url_for("dashboard"))

    headers = {
        "Authorization": f"Bearer {session['token']}"
    }

    # =========================================
    # Get My Reviews
    # =========================================

    response = requests.get(
        f"{API_URL}/reviewer/my-reviews",
        headers=headers
    )

    reviews = []

    if response.status_code == 200:
        reviews = response.json()

    # =========================================
    # Get Publications
    # =========================================

    response = requests.get(
        f"{API_URL}/publications/",
        headers=headers,
        params={
            "page": 1,
            "page_size": 100
        }
    )

    publications = []

    if response.status_code == 200:

        data = response.json()

        if isinstance(data, dict):
            publications = data.get("data", [])
        else:
            publications = data

    # =========================================
    # Create Publication ID -> Title Mapping
    # =========================================

    publication_map = {
        publication.get("id"): publication.get("title", "Untitled Publication")
        for publication in publications
    }

    # =========================================
    # Add Publication Title to Each Review
    # =========================================

    for review in reviews:

        publication_id = review.get("publication_id")

        review["publication_title"] = publication_map.get(
            publication_id,
            f"Publication #{publication_id}"
        )

    # =========================================
    # Render Reviewer Page
    # =========================================

    return render_template(
        "reviews.html",
        reviews=reviews
    )
@app.route("/review/<int:review_id>")
def review_details(review_id):

    if "token" not in session:
        return redirect(url_for("login"))

    # Allow Reviewer and System Admin
    if session.get("role") not in ["reviewer", "system_admin"]:
        return redirect(url_for("dashboard"))

    headers = {
        "Authorization": f"Bearer {session['token']}"
    }

    # =========================================
    # Get Reviews
    # =========================================

    if session.get("role") == "reviewer":

        # Reviewer can see only their own assignments
        response = requests.get(
            f"{API_URL}/reviewer/my-reviews",
            headers=headers
        )

        if response.status_code != 200:
            return redirect(url_for("reviewer"))

    else:

        # System Admin can see all review assignments
        response = requests.get(
            f"{API_URL}/reviewer/all-reviews",
            headers=headers
        )

        if response.status_code != 200:
            return redirect(url_for("review_management"))

    reviews = response.json()

    # =========================================
    # Find Requested Review
    # =========================================

    review = next(
        (
            r for r in reviews
            if r.get("id") == review_id
        ),
        None
    )

    if not review:

        if session.get("role") == "system_admin":
            return redirect(url_for("review_management"))

        return redirect(url_for("reviewer"))

    # =========================================
    # Get Publication Details
    # =========================================

    publication_id = review.get("publication_id")

    response = requests.get(
        f"{API_URL}/publications/{publication_id}",
        headers=headers
    )

    if response.status_code != 200:

        if session.get("role") == "system_admin":
            return redirect(url_for("review_management"))

        return redirect(url_for("reviewer"))

    publication = response.json()

    # =========================================
    # Get Researcher Details
    # =========================================

    researcher_name = "Unknown Researcher"

    researcher_id = publication.get("researcher_id")

    if researcher_id:

        response = requests.get(
            f"{API_URL}/researchers/{researcher_id}",
            headers=headers
        )

        if response.status_code == 200:

            researcher = response.json()

            researcher_name = (
                researcher.get("full_name")
                or researcher.get("name")
                or "Unknown Researcher"
            )

    # =========================================
    # Render Review Details
    # =========================================

    return render_template(
        "review_details.html",
        review=review,
        publication=publication,
        researcher_name=researcher_name,
        API_URL=API_URL
    )
@app.route("/review/<int:review_id>", methods=["POST"])
def submit_review(review_id):

    if "token" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "reviewer":
        return redirect(url_for("dashboard"))

    headers = {
        "Authorization": f"Bearer {session['token']}"
    }

    decision = request.form.get("decision")
    comments = request.form.get("comments")

    data = {
        "decision": decision,
        "comments": comments
    }

    response = requests.put(
        f"{API_URL}/reviewer/reviews/{review_id}",
        headers=headers,
        json=data
    )

    if response.status_code == 200:
        return redirect(
            url_for(
                "review_details",
                review_id=review_id
            )
        )

    return f"Failed to submit review: {response.text}", response.status_code

@app.route("/review-management")
def review_management():

    if "token" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "system_admin":
        return redirect(url_for("dashboard"))

    headers = {
        "Authorization": f"Bearer {session['token']}"
    }

    # =========================================
    # 1. Get ALL Publications
    # =========================================

    response = requests.get(
        f"{API_URL}/publications/",
        headers=headers,
        params={
            "page": 1,
            "page_size": 100
        }
    )

    all_publications = []

    if response.status_code == 200:

        data = response.json()

        if isinstance(data, dict):
            all_publications = data.get("data", [])
        elif isinstance(data, list):
            all_publications = data

    # =========================================
    # 2. Get ALL Reviewers
    # =========================================

    response = requests.get(
        f"{API_URL}/users",
        headers=headers
    )

    reviewers = []

    if response.status_code == 200:

        users = response.json()

        reviewers = [
            user
            for user in users
            if user.get("role") == "reviewer"
        ]

    # =========================================
    # 3. Get ALL Existing Reviews
    # =========================================

    response = requests.get(
        f"{API_URL}/reviewer/all-reviews",
        headers=headers
    )

    reviews = []

    if response.status_code == 200:

        data = response.json()

        if isinstance(data, list):
            reviews = data

        elif isinstance(data, dict):
            reviews = data.get("data", [])

    # =========================================
    # 4. Get Already Assigned Publication IDs
    # =========================================

    assigned_publication_ids = set()

    for review in reviews:

        publication_id = review.get("publication_id")

        if publication_id is not None:
            assigned_publication_ids.add(
                int(publication_id)
            )

    # =========================================
    # 5. ONLY Unassigned Submitted Publications
    # =========================================

    publications = []

    for publication in all_publications:

        publication_id = publication.get("id")

        if publication_id is None:
            continue

        publication_id = int(publication_id)

        # Must be Submitted
        if publication.get("status") != "Submitted":
            continue

        # Must NOT already have a reviewer
        if publication_id in assigned_publication_ids:
            continue

        publications.append(publication)

    # =========================================
    # 6. Publication Lookup
    # =========================================

    publication_map = {
        int(publication.get("id")): publication
        for publication in all_publications
        if publication.get("id") is not None
    }

    # =========================================
    # 7. Reviewer Lookup
    # =========================================

    reviewer_map = {
        int(reviewer.get("id")): reviewer
        for reviewer in reviewers
        if reviewer.get("id") is not None
    }

    # =========================================
    # 8. Prepare Review Assignment Display
    # =========================================

    formatted_reviews = []

    for review in reviews:

        publication_id = review.get("publication_id")
        reviewer_id = review.get("reviewer_id")

        publication = publication_map.get(
            int(publication_id)
        ) if publication_id is not None else None

        reviewer = reviewer_map.get(
            int(reviewer_id)
        ) if reviewer_id is not None else None

        formatted_reviews.append({

            "id": review.get("id"),

            "publication_id": publication_id,

            "publication_title": (
                publication.get("title")
                if publication
                else "Unknown Publication"
            ),

            "reviewer_id": reviewer_id,

            "reviewer_name": (
                reviewer.get("full_name")
                if reviewer
                else "Unknown Reviewer"
            ),

            "decision": review.get("decision"),

            "comments": review.get("comments"),

            "reviewed_at": review.get("reviewed_at")
        })

    # =========================================
    # 9. Render Page
    # =========================================

    return render_template(
        "review_management.html",
        publications=publications,
        reviewers=reviewers,
        reviews=formatted_reviews
    )

@app.route("/assign-review", methods=["POST"])
def assign_review():

    if "token" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "system_admin":
        return redirect(url_for("dashboard"))

    headers = {
        "Authorization": f"Bearer {session['token']}"
    }

    publication_id = request.form.get("publication_id")
    reviewer_id = request.form.get("reviewer_id")

    data = {
        "publication_id": int(publication_id),
        "reviewer_id": int(reviewer_id)
    }

    response = requests.post(
        f"{API_URL}/reviewer/assign",
        headers=headers,
        json=data
    )

    if response.status_code == 200:
        return redirect(
            url_for("review_management")
        )

    return (
        f"Failed to assign reviewer: {response.text}",
        response.status_code
    )
@app.route("/audit-logs")
def audit_logs():

    if "token" not in session:
        return redirect(url_for("login"))

    headers = {
        "Authorization": f"Bearer {session['token']}"
    }

    response = requests.get(
        f"{API_URL}/audit/logs",
        headers=headers
    )

    print(
        "GET AUDIT LOGS:",
        response.status_code,
        response.text
    )

    logs = []
    error = None

    if response.status_code == 200:

        logs = response.json()

    else:

        try:
            error = response.json().get(
                "detail",
                "Failed to load audit logs"
            )
        except Exception:
            error = "Failed to load audit logs"

    return render_template(
        "audit_logs.html",
        logs=logs,
        error=error
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