from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.project import ProjectMessage


def list_thread(db: Session, project_id: int, limit: int = 500) -> list[ProjectMessage]:
    stmt = (
        select(ProjectMessage)
        .where(ProjectMessage.project_id == project_id)
        .options(selectinload(ProjectMessage.sender))
        .order_by(ProjectMessage.created_at.asc())
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def get_by_id(db: Session, project_message_id: int) -> ProjectMessage | None:
    stmt = (
        select(ProjectMessage)
        .where(ProjectMessage.project_message_id == project_message_id)
        .options(selectinload(ProjectMessage.sender))
    )
    return db.scalar(stmt)