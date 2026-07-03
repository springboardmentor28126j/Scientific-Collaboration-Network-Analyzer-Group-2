from sqlalchemy.orm import Session
from app.models.publication import Publication, PublicationStatus

def get_publication_summary(db: Session):
    total = db.query(Publication).count()
    summary = {"total": total}
    for status in PublicationStatus:
        summary[status.value] = db.query(Publication).filter(Publication.status == status).count()
    return summary

# TODO: add functions for PDF export (reportlab) and Excel export (openpyxl)
