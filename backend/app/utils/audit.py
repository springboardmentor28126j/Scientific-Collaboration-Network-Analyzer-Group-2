from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog

def log_action(db: Session, user_id: int, action: str, details: str = None):
    """Helper function to create an audit log entry from anywhere in the backend."""
    log = AuditLog(user_id=user_id, action=action, details=details)
    db.add(log)
    db.commit()