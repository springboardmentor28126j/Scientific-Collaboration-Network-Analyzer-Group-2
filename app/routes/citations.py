from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db

router = APIRouter(
    prefix="/citations",
    tags=["Citations"]
)

@router.post("/", response_model=schemas.CitationResponse)
def create_citation(citation: schemas.CitationCreate, db: Session = Depends(get_db)):
    return crud.create_citation(db, citation)

@router.get("/", response_model=list[schemas.CitationResponse])
def get_citations(db: Session = Depends(get_db)):
    return crud.get_citations(db)
