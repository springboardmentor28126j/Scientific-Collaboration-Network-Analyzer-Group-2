from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.permissions import require_system_admin

router = APIRouter(prefix="/admin", tags=["Administration"])


@router.get("/data-quality")
def data_quality(_admin: models.User = Depends(require_system_admin), db: Session = Depends(get_db)):
    """Operational checklist for keeping research records trustworthy."""
    publications = db.query(models.Publication).all()
    researchers = db.query(models.Researcher).all()
    return {
        "summary": {
            "publications_missing_doi": sum(not item.doi for item in publications),
            "publications_without_authors": sum(not item.authors for item in publications),
            "researchers_without_institution": sum(not item.institution_id for item in researchers),
            "researchers_missing_email": sum(not item.email for item in researchers),
            "suspended_accounts": db.query(models.User).filter(models.User.account_status == "suspended").count(),
        },
        "issues": {
            "publications_missing_doi": [{"id": item.id, "title": item.title} for item in publications if not item.doi][:10],
            "publications_without_authors": [{"id": item.id, "title": item.title} for item in publications if not item.authors][:10],
            "researchers_without_institution": [{"id": item.id, "name": item.full_name} for item in researchers if not item.institution_id][:10],
            "researchers_missing_email": [{"id": item.id, "name": item.full_name} for item in researchers if not item.email][:10],
        },
    }
