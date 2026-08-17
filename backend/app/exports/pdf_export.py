import tempfile
import uuid
from pathlib import Path

from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Table
from reportlab.platypus import TableStyle
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


def _report_output_path(filename: str) -> str:
    """Writes generated report files to the OS temp directory instead of the
    backend's working directory, using a random suffix so two people
    downloading a report at the same time never read/write the same file."""
    unique_name = f"{filename.rsplit('.', 1)[0]}_{uuid.uuid4().hex[:8]}.{filename.rsplit('.', 1)[1]}"
    return str(Path(tempfile.gettempdir()) / unique_name)


def create_dashboard_pdf(summary, collaboration_status=None, top_collaborations=None,
                          institution_report=None, publication_year=None, publication_type=None,
                          publication_status=None, conference_type=None, user_roles=None,
                          departments=None, interests=None, skills=None):
    filename = _report_output_path("dashboard_report.pdf")
    document = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()
    elements = []

    table_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
    ])

    data = [
        ["Metric", "Value"],
        ["Total Users", summary.total_users],
        ["Total Researchers", summary.total_researchers],
        ["Total Institutions", summary.total_institutions],
        ["Total Publications", summary.total_publications],
        ["Total Conferences", summary.total_conferences],
        ["Total Sessions", summary.total_sessions],
        ["Total Participations", summary.total_participations],
        ["Total Collaborations", summary.total_collaborations],
    ]
    table = Table(data)
    table.setStyle(table_style)
    elements.append(table)

    def _add_section(title, rows, headers, fields):
        if not rows:
            return
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(title, styles["Heading2"]))
        elements.append(Spacer(1, 8))
        section_data = [headers] + [[getattr(r, f) for f in fields] for r in rows]
        t = Table(section_data)
        t.setStyle(table_style)
        elements.append(t)

    _add_section("Collaboration Requests by Status", collaboration_status,
                 ["Status", "Count"], ["request_status", "request_count"])
    _add_section("Top Collaborations", top_collaborations,
                 ["Researcher 1", "Researcher 2", "Shared Publications"],
                 ["researcher1_email", "researcher2_email", "strength"])
    _add_section("Institutions", institution_report,
                 ["Institution", "Researchers"], ["institution_name", "researcher_count"])
    _add_section("Publications by Year", publication_year, ["Year", "Count"],
                 ["year", "publication_count"])
    _add_section("Publications by Type", publication_type, ["Type", "Count"],
                 ["publication_type", "publication_count"])
    _add_section("Publications by Status", publication_status, ["Status", "Count"],
                 ["publication_status", "publication_count"])
    _add_section("Conferences by Type", conference_type, ["Type", "Count"],
                 ["conference_type", "conference_count"])
    _add_section("Users by Role", user_roles, ["Role", "Count"], ["role", "total_users"])
    _add_section("Departments", departments, ["Department", "Researchers"],
                 ["department", "total_researchers"])
    _add_section("Research Interests", interests, ["Interest", "Researchers"],
                 ["research_interest", "total_researchers"])
    _add_section("Skills", skills, ["Skill", "Researchers"], ["skill", "total_researchers"])

    document.build(elements)
    return filename


def create_compliance_pdf(report: dict) -> str:
    filename = _report_output_path("compliance_report.pdf")
    document = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()
    elements = []

    table_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
    ])

    elements.append(Paragraph(f"Compliance Report — {report['period']['start']} to {report['period']['end']}", styles["Heading1"]))
    elements.append(Spacer(1, 12))

    totals_data = [["Metric", "Count"]] + [[k.replace("_", " ").title(), v] for k, v in report["totals"].items()]
    t = Table(totals_data)
    t.setStyle(table_style)
    elements.append(t)

    def _add_section(title, rows, headers, keys):
        if not rows:
            return
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(title, styles["Heading2"]))
        elements.append(Spacer(1, 8))
        data = [headers] + [[str(r.get(k, "")) for k in keys] for r in rows]
        st = Table(data)
        st.setStyle(table_style)
        elements.append(st)

    _add_section("Publication Decisions", report["publication_decisions"], ["Date", "Action", "Reviewer", "Comment"], ["date", "action", "actor_email", "details"])
    _add_section("Login Failures", report["login_failures"], ["Date", "Attempted Email"], ["date", "attempted_email"])
    _add_section("MFA Events", report["mfa_events"], ["Date", "Action", "User"], ["date", "action", "actor_email"])

    document.build(elements)
    return filename