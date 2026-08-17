from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, selectinload

from app.api.deps import require_role
from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.user import User, UserRole
from app.schemas.audit_log import AuditLogListResponse, AuditLogOut

router = APIRouter()
ALLOWED_PAGE_SIZES = {10, 25, 50, 100}


@router.get("", response_model=AuditLogListResponse)
def list_audit_logs(
    entity_type: str | None = None,
    user_id: int | None = None,
    actor_user_id: int | None = None,
    action: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1),
    current_user: User = Depends(require_role(UserRole.SYSTEM_ADMIN)),
    db: Session = Depends(get_db),
) -> AuditLogListResponse:
    if page_size not in ALLOWED_PAGE_SIZES:
        page_size = 25

    query = db.query(AuditLog).options(selectinload(AuditLog.actor))
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if user_id is not None:
        query = query.filter(AuditLog.actor_user_id == user_id)
    if actor_user_id is not None:
        query = query.filter(AuditLog.actor_user_id == actor_user_id)
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

    items = []
    for row in rows:
        item = AuditLogOut.model_validate(row)
        item.actor_email = row.actor.email if row.actor else None
        items.append(item)

    return AuditLogListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/actions", response_model=list[str])
def list_audit_actions(
    current_user: User = Depends(require_role(UserRole.SYSTEM_ADMIN)),
    db: Session = Depends(get_db),
) -> list[str]:
    rows = db.query(AuditLog.action).distinct().order_by(AuditLog.action).all()
    return [row[0] for row in rows]