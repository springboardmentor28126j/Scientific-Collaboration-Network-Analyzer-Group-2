from sqlalchemy.orm import Session

from app.models import AuditLog


def record(db: Session, *, action: str, entity_type: str, entity_id: int | None = None, user_id: int | None = None, details: str | None = None) -> None:
    db.add(AuditLog(action=action, entity_type=entity_type, entity_id=entity_id, user_id=user_id, details=details))
    db.commit()
