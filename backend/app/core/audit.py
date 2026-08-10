"""Module 9: Audit & Compliance -- a single helper every route calls to
record an AuditLog row. Deliberately best-effort: a logging failure must
never break the request that triggered it, so any exception here is
swallowed after rolling back just the log insert (not the caller's own
transaction, which has typically already been committed by the time this
is called -- see call sites in routes/*.py).
"""
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def log_audit(
    db: Session,
    *,
    action: str,
    user_id: int | None = None,
    entity_type: str | None = None,
    entity_id: int | None = None,
    details: str | None = None,
) -> None:
    try:
        db.add(
            AuditLog(
                user_id=user_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                details=details,
            )
        )
        db.commit()
    except Exception:
        db.rollback()
