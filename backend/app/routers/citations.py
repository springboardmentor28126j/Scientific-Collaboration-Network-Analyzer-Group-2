from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter()

@router.get("/")
def list_citations(db: Session = Depends(get_db)):
    # TODO: implement
    return []
