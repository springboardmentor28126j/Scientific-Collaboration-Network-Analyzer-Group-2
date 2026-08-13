from sqlalchemy.orm import Session

from app.models import AuditLog


def client_ip(request) -> str | None:
    if not request:
        return None
    forwarded = request.headers.get("x-forwarded-for")
    return forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else None)


def record(db: Session, *, action: str, entity_type: str, entity_id: int | None = None, user_id: int | None = None, details: str | None = None, actor_role: str | None = None, ip_address: str | None = None, request=None) -> None:
    db.add(AuditLog(action=action, entity_type=entity_type, entity_id=entity_id, user_id=user_id, details=details, actor_role=actor_role, ip_address=ip_address or client_ip(request)))
    db.commit()
