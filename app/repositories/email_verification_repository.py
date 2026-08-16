from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.email_verification_token import EmailVerificationToken


def create_token(db: Session, user_id: int, token: str, expires_at: datetime) -> EmailVerificationToken:
    record = EmailVerificationToken(user_id=user_id, token=token, expires_at=expires_at)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_by_token(db: Session, token: str) -> EmailVerificationToken | None:
    return db.query(EmailVerificationToken).filter(EmailVerificationToken.token == token).first()


def mark_used(db: Session, record: EmailVerificationToken) -> None:
    record.used = True
    db.commit()


def invalidate_existing_tokens_for_user(db: Session, user_id: int) -> None:
    """Called before issuing a fresh token so old unused links stop working."""
    db.query(EmailVerificationToken).filter(
        EmailVerificationToken.user_id == user_id,
        EmailVerificationToken.used == False,  # noqa: E712
    ).update({"used": True})
    db.commit()


def is_expired(record: EmailVerificationToken) -> bool:
    expires_at = record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) > expires_at
