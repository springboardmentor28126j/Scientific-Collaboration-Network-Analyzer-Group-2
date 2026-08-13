from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app import models
from app.database import get_db
from app.permissions import require_system_admin

router = APIRouter(prefix="/audit-logs", tags=["Audit logs"])


@router.get("/")
def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    action: str | None = None,
    entity_type: str | None = None,
    _admin: models.User = Depends(require_system_admin),
    db: Session = Depends(get_db),
):
    query = db.query(models.AuditLog).options(joinedload(models.AuditLog.user))
    if action:
        query = query.filter(models.AuditLog.action.ilike(f"%{action.strip()}%"))
    if entity_type:
        query = query.filter(models.AuditLog.entity_type == entity_type)
    total = query.count()
    rows = query.order_by(models.AuditLog.created_at.desc(), models.AuditLog.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": [{
            "id": row.id, "action": row.action, "entity_type": row.entity_type,
            "entity_id": row.entity_id, "details": row.details,
            "actor": row.user.name if row.user else "System", "role": row.actor_role or (row.user.role if row.user else "System"), "ip_address": row.ip_address,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        } for row in rows],
        "page": page, "page_size": page_size, "total": total,
    }
