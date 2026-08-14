from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from typing import Optional
from app.database import get_db
from app.models.audit_log import AuditLog

router = APIRouter()


@router.get("/logs")
def list_audit_logs(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("timestamp", regex="^(id|action|timestamp)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    action: Optional[str] = None,
    user_id: Optional[int] = None
):
    query = db.query(AuditLog)

    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)

    sort_column = getattr(AuditLog, sort_by)
    if order == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    total = query.count()
    offset = (page - 1) * limit
    logs = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit,
        "logs": logs
    }


@router.post("/")
def create_audit_log(user_id: int, action: str, details: str = None, db: Session = Depends(get_db)):
    log = AuditLog(user_id=user_id, action=action, details=details)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log