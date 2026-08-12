from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app import crud

from app.schemas.audit_log import AuditLogResponse


router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"]
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.get(
    "/",
    response_model=list[AuditLogResponse]
)
def get_all_audit_logs(
    db: Session = Depends(get_db)
):

    return crud.get_all_audit_logs(db)


@router.get(
    "/user/{user_id}",
    response_model=list[AuditLogResponse]
)
def get_user_audit_logs(
    user_id: int,
    db: Session = Depends(get_db)
):

    return crud.get_audit_logs_by_user(
        db,
        user_id
    )