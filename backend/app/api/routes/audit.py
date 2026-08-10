from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, selectinload

from app.api.deps import require_role
from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.user import User, UserRole
from app.schemas.audit_log import AuditLogOut, AuditLogPage

router = APIRouter()

ALLOWED_PAGE_SIZES = {10, 25, 50, 100}


@router.get("", response_model=AuditLogPage)
def list_audit_logs(
    entity_type: str | None = None,
    user_id: int | None = None,
    action: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(25),
    current_user: User = Depends(require_role(UserRole.SYSTEM_ADMIN)),
    db: Session = Depends(get_db),
) -> AuditLogPage:
    if page_size not in ALLOWED_PAGE_SIZES:
        page_size = 25

    query = db.query(AuditLog).options(selectinload(AuditLog.user))
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if user_id is not None:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if date_from is not None:
        query = query.filter(AuditLog.created_at >= date_from)
    if date_to is not None:
        query = query.filter(AuditLog.created_at <= date_to)

    total = query.count()
    rows = (
        query.order_by(AuditLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = [
        AuditLogOut(
            id=row.id,
            user_id=row.user_id,
            user_email=row.user.email if row.user else None,
            action=row.action,
            entity_type=row.entity_type,
            entity_id=row.entity_id,
            details=row.details,
            created_at=row.created_at,
        )
        for row in rows
    ]
    return AuditLogPage(items=items, total=total)


@router.get("/actions", response_model=list[str])
def list_audit_actions(
    current_user: User = Depends(require_role(UserRole.SYSTEM_ADMIN)),
    db: Session = Depends(get_db),
) -> list[str]:
    """Distinct action values seen so far, for populating the filter
    dropdown on the Audit Log page without hardcoding the list."""
    rows = db.query(AuditLog.action).distinct().order_by(AuditLog.action).all()
    return [row[0] for row in rows]
