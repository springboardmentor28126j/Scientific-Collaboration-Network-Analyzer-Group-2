from flask import send_file
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = "your-secret-key-change-this"

API_URL = "http://127.0.0.1:8000"

def get_unread_count():
    try:
        response = requests.get(f"{API_URL}/notifications/unread-count")
        if response.status_code == 200:
            return response.json().get("unread_count", 0)
    except requests.exceptions.ConnectionError:
        pass
    return 0


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
        response = requests.get(f"{API_URL}/publications/", params={'limit': 100})
        if response.status_code == 200:
            result = response.json()
            pubs = result.get('publications', [])
            pub_count = result.get('total', len(pubs))
            recent_pubs = pubs[:3]  # sabse recent 3 (already sorted desc by id)
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

    # Collaborations count fetch karo
    collaborations_count = 0
    try:
        response = requests.get(f"{API_URL}/collaborations/")
        if response.status_code == 200:
            collabs = response.json()
            collaborations_count = len(collabs)
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
            collaborations_count=collaborations_count,
            recent_pubs=recent_pubs,
            unread_count=get_unread_count()
        )
    
@app.route("/notifications")
def notifications_page():
    if "token" not in session:
        return redirect(url_for("login"))

    try:
        response = requests.get(f"{API_URL}/notifications/")
        notifs = response.json() if response.status_code == 200 else []
    except requests.exceptions.ConnectionError:
        notifs = []

    try:
        requests.put(f"{API_URL}/notifications/mark-all-read")
    except requests.exceptions.ConnectionError:
        pass

    return render_template("notifications.html", notifications=notifs)
     
@app.route("/publications")
def publications():
    if "token" not in session:
        return redirect(url_for("login"))

    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort_by', 'id')
    order = request.args.get('order', 'desc')

    params = {
        'page': page,
        'limit': 3,
        'sort_by': sort_by,
        'order': order
    }

    try:
        response = requests.get(f"{API_URL}/publications/", params=params)
        result = response.json() if response.status_code == 200 else {}
    except requests.exceptions.ConnectionError:
        result = {}

    pubs = result.get('publications', [])
    total_pages = result.get('total_pages', 1)
    current_page = result.get('page', 1)

    # Researchers ka data fetch karo taaki author name dikha sakein
    try:
        r_response = requests.get(f"{API_URL}/researchers/")
        researchers = r_response.json() if r_response.status_code == 200 else []
        researcher_map = {r["id"]: r["full_name"] for r in researchers}
    except requests.exceptions.ConnectionError:
        researcher_map = {}

    for pub in pubs:
        pub["author_name"] = researcher_map.get(pub.get("author_id"), "Unknown")

        try:
            c_response = requests.get(f"{API_URL}/citations/publication/{pub['id']}")
            if c_response.status_code == 200:
                pub["cited_count"] = c_response.json().get("cited_by_count", 0)
            else:
                pub["cited_count"] = 0
        except requests.exceptions.ConnectionError:
            pub["cited_count"] = 0

    return render_template(
        "publications.html",
        publications=pubs,
        total_pages=total_pages,
        current_page=current_page,
        sort_by=sort_by,
        order=order
    )

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

@app.route("/publications/delete/<int:pub_id>")
def delete_publication(pub_id):
    if "token" not in session:
        return redirect(url_for("login"))

    try:
        requests.delete(f"{API_URL}/publications/{pub_id}")
    except requests.exceptions.ConnectionError:
        pass

    return redirect(url_for("publications"))
# ===== CITATIONS ROUTES =====

@app.route('/citations')
def citations():
    token = session.get('token')
    headers = {'Authorization': f'Bearer {token}'} if token else {}

    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort_by', 'id')
    order = request.args.get('order', 'desc')
    citation_style = request.args.get('citation_style', '')
    year = request.args.get('year', '')
    search = request.args.get('search', '')

    params = {
        'page': page,
        'limit': 2,
        'sort_by': sort_by,
        'order': order
    }
    if citation_style:
        params['citation_style'] = citation_style
    if year:
        params['year'] = year
    if search:
        params['search'] = search

    try:
        response = requests.get(f'{API_URL}/citations/', headers=headers, params=params)
        result = response.json() if response.status_code == 200 else {}
    except:
        result = {}

    citations_data = result.get('citations', [])
    total_pages = result.get('total_pages', 1)
    current_page = result.get('page', 1)

    return render_template('citations.html', 
        citations=citations_data,
        total_pages=total_pages,
        current_page=current_page,
        sort_by=sort_by,
        order=order,
        citation_style=citation_style,
        year=year,
        search=search
    )
@app.route('/add_citation', methods=['GET', 'POST'])
def add_citation():
    if "token" not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        token = session.get('token')
        headers = {'Authorization': f'Bearer {token}'} if token else {}
        
        data = {
            'citing_publication_id': int(request.form.get('citing_publication_id', 0)),
            'cited_publication_id': int(request.form.get('cited_publication_id', 0)),
            'title': request.form.get('title', ''),
            'authors': request.form.get('authors', ''),
            'journal': request.form.get('journal', ''),
            'year': int(request.form.get('year')) if request.form.get('year') else None,
            'doi': request.form.get('doi', ''),
            'citation_style': request.form.get('citation_style', 'APA'),
            'formatted_citation': request.form.get('formatted_citation', '')
        }
        
        try:
            response = requests.post(f'{API_URL}/citations/', json=data, headers=headers)
            print(f"DEBUG: Status: {response.status_code}")
            print(f"DEBUG: Response: {response.text}")
            if response.status_code == 200:
                return redirect(url_for('citations'))
        except Exception as e:
            print(f"DEBUG: Error: {str(e)}")
    
    return render_template('add_citation.html')
@app.route('/edit_citation/<int:citation_id>', methods=['GET', 'POST'])
def edit_citation(citation_id):
    if 'access_token' not in session:
        return redirect(url_for('login'))
    
    token = session['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Get citation
    try:
        response = requests.get(f'{API_URL}/citations/{citation_id}', headers=headers)
        citation = response.json() if response.status_code == 200 else None
    except:
        citation = None
    
    if not citation:
        return redirect(url_for('citations'))
    
    if request.method == 'POST':
        data = {
            'title': request.form.get('title', ''),
            'authors': request.form.get('authors', ''),
            'journal': request.form.get('journal', ''),
            'year': int(request.form.get('year')) if request.form.get('year') else None,
            'doi': request.form.get('doi', ''),
            'citation_style': request.form.get('citation_style', 'APA'),
            'formatted_citation': request.form.get('formatted_citation', '')
        }
        
        try:
            response = requests.put(f'{API_URL}/citations/{citation_id}', json=data, headers=headers)
            if response.status_code == 200:
                return redirect(url_for('citations'))
        except Exception as e:
            print(f'Error: {e}')
    
    return render_template('edit_citation.html', citation=citation)


@app.route('/delete_citation/<int:citation_id>')
def delete_citation(citation_id):
    if 'access_token' not in session:
        return redirect(url_for('login'))
    
    token = session['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        requests.delete(f'{API_URL}/citations/{citation_id}', headers=headers)
    except:
        pass
    
    return redirect(url_for('citations'))
@app.route("/conferences")
def conferences():
    if "token" not in session:
        return redirect(url_for("login"))

    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort_by', 'id')
    order = request.args.get('order', 'desc')

    params = {
        'page': page,
        'limit': 3,
        'sort_by': sort_by,
        'order': order
    }

    try:
        response = requests.get(f"{API_URL}/conferences/", params=params)
        result = response.json() if response.status_code == 200 else {}
    except requests.exceptions.ConnectionError:
        result = {}

    confs = result.get('conferences', [])
    total_pages = result.get('total_pages', 1)
    current_page = result.get('page', 1)

    return render_template(
        "conferences.html",
        conferences=confs,
        total_pages=total_pages,
        current_page=current_page,
        sort_by=sort_by,
        order=order
    )

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

    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort_by', 'id')
    order = request.args.get('order', 'desc')

    params = {
        'page': page,
        'limit': 3,
        'sort_by': sort_by,
        'order': order
    }

    try:
        response = requests.get(f"{API_URL}/institutions/", params=params)
        result = response.json() if response.status_code == 200 else {}
    except requests.exceptions.ConnectionError:
        result = {}

    insts = result.get('institutions', [])
    total_pages = result.get('total_pages', 1)
    current_page = result.get('page', 1)

    return render_template(
        "institutions.html",
        institutions=insts,
        total_pages=total_pages,
        current_page=current_page,
        sort_by=sort_by,
        order=order
    )
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
@app.route("/collaborations")
def collaborations():
    if "token" not in session:
        return redirect(url_for("login"))

    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort_by', 'id')
    order = request.args.get('order', 'desc')

    params = {
        'page': page,
        'limit': 3,
        'sort_by': sort_by,
        'order': order
    }

    try:
        response = requests.get(f"{API_URL}/collaborations/", params=params)
        result = response.json() if response.status_code == 200 else {}
    except requests.exceptions.ConnectionError:
        result = {}

    collabs = result.get('collaborations', [])
    total_pages = result.get('total_pages', 1)
    current_page = result.get('page', 1)

    return render_template(
        "collaborations.html",
        collaborations=collabs,
        total_pages=total_pages,
        current_page=current_page,
        sort_by=sort_by,
        order=order
    )

@app.route("/collaborations/add", methods=["GET", "POST"])
def add_collaboration():
    if "token" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        project_name = request.form.get("project_name")
        institution_a = request.form.get("institution_a")
        institution_b = request.form.get("institution_b")
        description = request.form.get("description")

        try:
            response = requests.post(
                f"{API_URL}/collaborations/",
                json={
                    "project_name": project_name,
                    "institution_a": institution_a,
                    "institution_b": institution_b,
                    "description": description
                }
            )
            if response.status_code == 200:
                return redirect(url_for("collaborations"))
            else:
                return render_template("add_collaboration.html", error="Something went wrong")
        except requests.exceptions.ConnectionError:
            return render_template("add_collaboration.html", error="Cannot connect to server")

    return render_template("add_collaboration.html")
@app.route("/reports")
def reports():
    if "token" not in session:
        return redirect(url_for("login"))

    try:
        response = requests.get(f"{API_URL}/reports/summary")
        summary = response.json() if response.status_code == 200 else {}
    except requests.exceptions.ConnectionError:
        summary = {}

    return render_template("reports.html", summary=summary)


@app.route("/reports/export/publications")
def export_publications():
    if "token" not in session:
        return redirect(url_for("login"))

    try:
        response = requests.get(f"{API_URL}/reports/publications/export/csv")
        from flask import Response
        return Response(
            response.content,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=publications_report.csv"}
        )
    except requests.exceptions.ConnectionError:
        return redirect(url_for("reports"))
@app.route('/report/<report_type>')
def view_report(report_type):
    token = session.get('token')
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    
    try:
        response = requests.get(f'{API_URL}/reports/type/{report_type}', headers=headers)
        reports_data = response.json() if response.status_code == 200 else []
    except Exception as e:
        reports_data = []

    # Chart data set karo report type ke hisaab se
    chart_configs = {
        'publication': {
            'title': 'Publication Trends',
            'labels': ['2021', '2022', '2023', '2024'],
            'data': [3, 2, 4, 6],
            'label': 'Publications'
        },
        'research': {
            'title': 'Research Activity',
            'labels': ['2021', '2022', '2023', '2024'],
            'data': [2, 3, 5, 4],
            'label': 'Research Projects'
        },
        'collaboration': {
            'title': 'Collaboration Growth',
            'labels': ['2021', '2022', '2023', '2024'],
            'data': [1, 2, 2, 3],
            'label': 'Collaborations'
        },
        'institution': {
            'title': 'Institution Partnerships',
            'labels': ['2021', '2022', '2023', '2024'],
            'data': [1, 1, 2, 3],
            'label': 'Institutions'
        }
    }

    chart_info = chart_configs.get(report_type, {
        'title': 'Activity Trend',
        'labels': ['2021', '2022', '2023', '2024'],
        'data': [1, 2, 3, 4],
        'label': 'Records'
    })

    return render_template(
        'view_report.html',
        reports=reports_data,
        report_type=report_type,
        chart_title=chart_info['title'],
        chart_labels=chart_info['labels'],
        chart_data=chart_info['data'],
        chart_label=chart_info['label']
    )

@app.route('/report/<report_type>/export/pdf')
def export_report_pdf(report_type):
    if "token" not in session:
        return redirect(url_for('login'))
    
    token = session.get('token')
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    
    try:
        response = requests.get(f'{API_URL}/reports/type/{report_type}', headers=headers)
        reports_data = response.json() if response.status_code == 200 else []
    except:
        reports_data = []
    
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#111827'),
        spaceAfter=30,
        alignment=1
    )
    
    title = Paragraph(f"{report_type.upper()} Report", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.3*inch))
    
    if reports_data:
        for report in reports_data:
            data = [
                ['Field', 'Value'],
                ['Title', report.get('title', 'N/A')],
                ['Description', report.get('description', 'N/A')],
                ['Total Count', str(report.get('total_count', 0))],
                ['Year Range', report.get('year_range', 'N/A')],
                ['Summary', report.get('summary', 'N/A')]
            ]
            
            table = Table(data, colWidths=[2*inch, 4*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 0.5*inch))
    
    doc.build(elements)
    pdf_buffer.seek(0)
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'{report_type}_report.pdf'
    )
@app.route('/report/<report_type>/export/excel')
def export_report_excel(report_type):
    if "token" not in session:
        return redirect(url_for('login'))
    
    token = session.get('token')
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    
    try:
        response = requests.get(f'{API_URL}/reports/type/{report_type}', headers=headers)
        reports_data = response.json() if response.status_code == 200 else []
    except:
        reports_data = []
    
    wb = Workbook()
    ws = wb.active
    ws.title = f"{report_type} Report"
    
    headers_list = ['Title', 'Description', 'Total Count', 'Year Range', 'Summary']
    ws.append(headers_list)
    
    for report in reports_data:
        ws.append([
            report.get('title', ''),
            report.get('description', ''),
            report.get('total_count', 0),
            report.get('year_range', ''),
            report.get('summary', '')
        ])
    
    excel_buffer = BytesIO()
    wb.save(excel_buffer)
    excel_buffer.seek(0)
    
    return send_file(
        excel_buffer,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'{report_type}_report.xlsx'
    )
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)