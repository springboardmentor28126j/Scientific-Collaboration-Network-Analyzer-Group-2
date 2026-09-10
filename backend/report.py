from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Researcher, Publication, Collaboration


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


@router.get("/")
def get_reports(db: Session = Depends(get_db)):

    researcher_count = db.query(Researcher).count()
    publication_count = db.query(Publication).count()
    collaboration_count = db.query(Collaboration).count()

    return {
        "researchers": researcher_count,
        "publications": publication_count,
        "collaborations": collaboration_count
    }