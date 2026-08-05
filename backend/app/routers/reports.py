from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.publication import Publication, PublicationStatus
from app.models.conference import Conference
from app.models.collaboration import Collaboration
from app.models.institution import Institution
import io
import csv
from datetime import datetime

router = APIRouter()


@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    total_publications = db.query(Publication).count()
    total_conferences = db.query(Conference).count()
    total_collaborations = db.query(Collaboration).count()
    total_institutions = db.query(Institution).count()

    status_breakdown = {}
    for status in PublicationStatus:
        count = db.query(Publication).filter(Publication.status == status).count()
        status_breakdown[status.value] = count

    return {
        "total_publications": total_publications,
        "total_conferences": total_conferences,
        "total_collaborations": total_collaborations,
        "total_institutions": total_institutions,
        "publication_status_breakdown": status_breakdown,
        "generated_at": datetime.utcnow().isoformat()
    }


@router.get("/publications/export/csv")
def export_publications_csv(db: Session = Depends(get_db)):
    publications = db.query(Publication).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Title", "Type", "Status", "DOI", "Author ID"])

    for pub in publications:
        writer.writerow([pub.id, pub.title, pub.type.value, pub.status.value, pub.doi or "", pub.author_id])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=publications_report.csv"}
    )