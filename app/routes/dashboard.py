from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import crud, auth
from app.database import get_db

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
    dependencies=[Depends(auth.require_authenticated)]
)

@router.get("/")
def get_dashboard(db: Session = Depends(get_db)):
    return {
        "total_researchers": crud.count_researchers(db),
        "total_institutions": crud.count_institutions(db),
        "total_publications": crud.count_publications(db),
        "total_conferences": crud.get_conferences(db).__len__(),
        "total_collaborations": crud.count_collaborations(db),
        "total_citations": crud.count_citations(db),
        "total_projects": crud.count_projects(db),
    }
