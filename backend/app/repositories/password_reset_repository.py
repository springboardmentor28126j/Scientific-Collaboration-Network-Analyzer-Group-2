from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.password_reset_token import PasswordResetToken


def create_token(db: Session, user_id: int, token: str, expires_at: datetime) -> PasswordResetToken:
    record = PasswordResetToken(user_id=user_id, token=token, expires_at=expires_at)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_by_token(db: Session, token: str) -> PasswordResetToken | None:
    return db.query(PasswordResetToken).filter(PasswordResetToken.token == token).first()


def mark_used(db: Session, record: PasswordResetToken) -> None:
    record.used = True
    db.commit()


def invalidate_existing_tokens_for_user(db: Session, user_id: int) -> None:
    """Called before issuing a fresh token so old unused reset links stop working."""
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user_id,
        PasswordResetToken.used == False,  # noqa: E712
    ).update({"used": True})
    db.commit()


def is_expired(record: PasswordResetToken) -> bool:
    expires_at = record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) > expires_at
