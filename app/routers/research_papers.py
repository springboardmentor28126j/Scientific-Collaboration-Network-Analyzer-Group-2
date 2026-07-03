from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app import crud
from app.schemas.research_paper import ResearchPaperCreate, ResearchPaperResponse

router = APIRouter(prefix="/papers", tags=["Research Papers"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[ResearchPaperResponse])
def get_papers(db: Session = Depends(get_db)):
    return crud.get_all_papers(db)


@router.post("/", response_model=ResearchPaperResponse)
def add_paper(paper: ResearchPaperCreate, db: Session = Depends(get_db)):
    return crud.create_paper(db, paper)