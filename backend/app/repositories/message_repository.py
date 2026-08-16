from sqlalchemy import select, update
from sqlalchemy.orm import Session, selectinload

from app.models.collaboration import Collaboration
from app.models.message import Message


def get_by_id(db: Session, message_id: int) -> Message | None:
    stmt = select(Message).where(Message.message_id == message_id).options(selectinload(Message.sender))
    return db.scalar(stmt)


def list_thread(db: Session, collaboration_id: int, limit: int = 500) -> list[Message]:
    """Oldest-first, like reading down a chat log. limit is a hard safety
    cap, not real pagination -- fine for a 1:1 thread at this data scale."""
    stmt = (
        select(Message)
        .where(Message.collaboration_id == collaboration_id)
        .options(selectinload(Message.sender))
        .order_by(Message.created_at.asc())
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def mark_thread_read(db: Session, collaboration_id: int, reader_researcher_id: int) -> None:
    """Marks every message in this thread NOT sent by the reader as read --
    fired as a side effect of opening the thread, same as most chat apps
    mark-as-read on open rather than requiring an explicit action."""
    db.execute(
        update(Message)
        .where(
            Message.collaboration_id == collaboration_id,
            Message.sender_id != reader_researcher_id,
            Message.is_read.is_(False),
        )
        .values(is_read=True)
    )
    db.commit()


def unread_count(db: Session, researcher_id: int) -> int:
    stmt = (
        select(Message.message_id)
        .join(Collaboration, Collaboration.collaboration_id == Message.collaboration_id)
        .where(
            Message.is_read.is_(False),
            Message.sender_id != researcher_id,
            (Collaboration.researcher1_id == researcher_id) | (Collaboration.researcher2_id == researcher_id),
        )
    )
    return len(list(db.scalars(stmt).all()))


def unread_count_for_collaboration(db: Session, collaboration_id: int, researcher_id: int) -> int:
    stmt = select(Message.message_id).where(
        Message.collaboration_id == collaboration_id,
        Message.is_read.is_(False),
        Message.sender_id != researcher_id,
    )
    return len(list(db.scalars(stmt).all()))