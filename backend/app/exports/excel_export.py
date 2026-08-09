from openpyxl import Workbook
from openpyxl.styles import Font


def create_dashboard_excel(summary, collaboration_status=None, top_collaborations=None):
    workbook = Workbook()

    sheet = workbook.active
    sheet.title = "Dashboard Report"

    sheet.append(["Metric", "Value"])

    bold = Font(bold=True)
    sheet["A1"].font = bold
    sheet["B1"].font = bold

    data = [
        ("Total Users", summary.total_users),
        ("Total Researchers", summary.total_researchers),
        ("Total Institutions", summary.total_institutions),
        ("Total Publications", summary.total_publications),
        ("Total Conferences", summary.total_conferences),
        ("Total Sessions", summary.total_sessions),
        ("Total Participations", summary.total_participations),
        ("Total Collaborations", summary.total_collaborations),
    ]

    for row in data:
        sheet.append(row)

    if collaboration_status:
        status_sheet = workbook.create_sheet("Collaboration Requests")
        status_sheet.append(["Status", "Count"])
        status_sheet["A1"].font = bold
        status_sheet["B1"].font = bold
        for row in collaboration_status:
            status_sheet.append([row.request_status, row.request_count])

    if top_collaborations:
        top_sheet = workbook.create_sheet("Top Collaborations")
        top_sheet.append(["Researcher 1", "Researcher 2", "Shared Publications"])
        top_sheet["A1"].font = bold
        top_sheet["B1"].font = bold
        top_sheet["C1"].font = bold
        for row in top_collaborations:
            top_sheet.append([row.researcher1_email, row.researcher2_email, row.strength])

    filename = "dashboard_report.xlsx"
    workbook.save(filename)

    return filename