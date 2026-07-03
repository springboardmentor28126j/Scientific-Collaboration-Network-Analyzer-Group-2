from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter()

@router.get("/logs")
def list_audit_logs(db: Session = Depends(get_db)):
    # TODO: implement
    return []
