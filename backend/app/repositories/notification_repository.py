from sqlalchemy import select, func, desc
from sqlalchemy.orm import Session

from app.models.notification import Notification


def list_for_user(
    db: Session, user_id: int, unread_only: bool = False, page: int = 1, page_size: int = 20
) -> tuple[list[Notification], int]:
    stmt = select(Notification).where(Notification.user_id == user_id)
    if unread_only:
        stmt = stmt.where(Notification.is_read.is_(False))

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))

    stmt = stmt.order_by(desc(Notification.created_at)).offset((page - 1) * page_size).limit(page_size)
    items = list(db.scalars(stmt).all())
    return items, total


def count_unread(db: Session, user_id: int) -> int:
    return db.scalar(
        select(func.count()).select_from(Notification).where(
            Notification.user_id == user_id, Notification.is_read.is_(False)
        )
    )
