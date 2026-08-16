from sqlalchemy import select, func, desc
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def list_audit_logs(
    db: Session,
    user_id: int | None = None,
    entity_type: str | None = None,
    action: str | None = None,
    page: int = 1,
    page_size: int = 25,
) -> tuple[list[AuditLog], int]:
    stmt = select(AuditLog)
    if user_id is not None:
        stmt = stmt.where(AuditLog.user_id == user_id)
    if entity_type is not None:
        stmt = stmt.where(AuditLog.entity_type == entity_type)
    if action is not None:
        stmt = stmt.where(AuditLog.action == action)

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))

    stmt = stmt.order_by(desc(AuditLog.created_at)).offset((page - 1) * page_size).limit(page_size)
    items = list(db.scalars(stmt).all())
    return items, total


def count_all(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(AuditLog))
