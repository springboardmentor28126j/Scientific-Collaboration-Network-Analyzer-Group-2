from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.researcher import ResearcherCreate, ResearcherOut

router = APIRouter()

@router.post("/", response_model=ResearcherOut)
def create_researcher(researcher: ResearcherCreate, db: Session = Depends(get_db)):
    # TODO: implement
    pass

@router.get("/{researcher_id}", response_model=ResearcherOut)
def get_researcher(researcher_id: int, db: Session = Depends(get_db)):
    # TODO: implement
    pass
