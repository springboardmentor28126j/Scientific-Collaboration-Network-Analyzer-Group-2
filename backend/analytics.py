from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Researcher, Publication, Collaboration, Conference


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.get("/")
def get_analytics(db: Session = Depends(get_db)):

    total_researchers = db.query(Researcher).count()
    total_publications = db.query(Publication).count()
    total_collaborations = db.query(Collaboration).count()
    total_conferences = db.query(Conference).count()

    return {
        "total_researchers": total_researchers,
        "total_publications": total_publications,
        "total_collaborations": total_collaborations,
        "total_conferences": total_conferences
    }