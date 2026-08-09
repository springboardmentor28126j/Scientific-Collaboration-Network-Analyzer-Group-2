from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Table
from reportlab.platypus import TableStyle
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


def create_dashboard_pdf(summary, collaboration_status=None, top_collaborations=None):
    filename = "dashboard_report.pdf"

    document = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()
    elements = []

    table_style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ]
    )

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

    if collaboration_status:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Collaboration Requests by Status", styles["Heading2"]))
        elements.append(Spacer(1, 8))
        status_data = [["Status", "Count"]] + [
            [row.request_status, row.request_count] for row in collaboration_status
        ]
        status_table = Table(status_data)
        status_table.setStyle(table_style)
        elements.append(status_table)

    if top_collaborations:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Top Collaborations", styles["Heading2"]))
        elements.append(Spacer(1, 8))
        top_data = [["Researcher 1", "Researcher 2", "Shared Publications"]] + [
            [row.researcher1_email, row.researcher2_email, row.strength] for row in top_collaborations
        ]
        top_table = Table(top_data)
        top_table.setStyle(table_style)
        elements.append(top_table)

    document.build(elements)
    return filename