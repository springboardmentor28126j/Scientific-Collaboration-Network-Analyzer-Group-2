import io
import csv
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

# ReportLab imports for PDF creation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Apne project ki dependencies aur models import karein
# from app.db.session import get_db
# from app.models import User, Publication, Institution

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/summary")
def get_report_summary():
    """Dashboard analytics aur metrics ke liye summary data."""
    # Note: Asli database metrics ke saath replace karein
    return {
        "total_researchers": 142,
        "total_publications": 389,
        "total_institutions": 28,
        "total_citations": 4120,
        "recent_activities": [
            {"date": "2026-08-01", "event": "New Publication added by Dr. Sharma"},
            {"date": "2026-07-30", "event": "IIT Bombay joined the network"},
            {"date": "2026-07-28", "event": "15 new researchers registered"},
        ],
        "top_domains": [
            {"domain": "Artificial Intelligence", "count": 120},
            {"domain": "Data Science", "count": 95},
            {"domain": "Quantum Computing", "count": 45},
            {"domain": "Biotechnology", "count": 68},
        ]
    }


@router.get("/export/csv")
def export_csv_report():
    """Researchers & Publications ka CSV Report Download."""
    # Output stream setup
    stream = io.StringIO()
    writer = csv.writer(stream)

    # Headers
    writer.writerow(["SCNA Network Summary Report", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"])
    writer.writerow([])
    writer.writerow(["Category", "Metric / Detail", "Count / Status"])

    # Sample data rows (Yahan DB queries lagayein)
    writer.writerow(["Overview", "Total Researchers", 142])
    writer.writerow(["Overview", "Total Publications", 389])
    writer.writerow(["Overview", "Total Institutions", 28])
    writer.writerow(["Overview", "Total Citations", 4120])
    writer.writerow([])
    writer.writerow(["Domain Breakdown", "Artificial Intelligence", 120])
    writer.writerow(["Domain Breakdown", "Data Science", 95])
    writer.writerow(["Domain Breakdown", "Biotechnology", 68])
    writer.writerow(["Domain Breakdown", "Quantum Computing", 45])

    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename=SCNA_Report_{datetime.now().strftime('%Y%m%d')}.csv"
    return response


@router.get("/export/pdf")
def export_pdf_report():
    """Formatted PDF Report Download using ReportLab."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor("#0d6efd"), spaceAfter=10)
    normal_style = styles['Normal']

    # Document Header
    story.append(Paragraph("<b>Scientific Collaboration Network Analyzer (SCNA)</b>", title_style))
    story.append(Paragraph(f"<b>System Analytics & Report</b> — Generated on: {datetime.now().strftime('%d %b %Y, %H:%M')}", normal_style))
    story.append(Spacer(1, 15))

    # Metrics Table
    data = [
        ["Metric Category", "Value / Count", "Status"],
        ["Total Researchers", "142 Active", "Growing (+12%)"],
        ["Total Publications", "389 Papers", "High Activity"],
        ["Partner Institutions", "28 Universities", "Stable"],
        ["Total Citations", "4,120 Citations", "Top Tier"],
    ]

    table = Table(data, colWidths=[200, 150, 150])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
    ]))

    story.append(table)
    story.append(Spacer(1, 20))

    # Second Section: Recent Updates
    story.append(Paragraph("<b>Top Research Domains Breakdown:</b>", styles['Heading2']))
    story.append(Spacer(1, 5))
    
    domain_data = [
        ["Domain", "Publications Count", "Share %"],
        ["Artificial Intelligence", "120", "36.5%"],
        ["Data Science", "95", "28.9%"],
        ["Biotechnology", "68", "20.7%"],
        ["Quantum Computing", "45", "13.9%"],
    ]
    
    table2 = Table(domain_data, colWidths=[200, 150, 150])
    table2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#495057')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
    ]))
    story.append(table2)

    doc.build(story)
    buffer.seek(0)

    response = StreamingResponse(buffer, media_type="application/pdf")
    response.headers["Content-Disposition"] = f"attachment; filename=SCNA_Analytics_Report_{datetime.now().strftime('%Y%m%d')}.pdf"
    return response