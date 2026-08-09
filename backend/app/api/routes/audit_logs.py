from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.user import User, UserRole
from app.schemas.audit_log import AuditLogListResponse, AuditLogOut

router = APIRouter()


@router.get("", response_model=AuditLogListResponse)
def list_audit_logs(
    action: str | None = None,
    entity_type: str | None = None,
    actor_user_id: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_role(UserRole.SYSTEM_ADMIN)),
    db: Session = Depends(get_db),
) -> AuditLogListResponse:
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if actor_user_id:
        query = query.filter(AuditLog.actor_user_id == actor_user_id)

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