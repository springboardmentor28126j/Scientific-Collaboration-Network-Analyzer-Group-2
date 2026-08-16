from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.collaboration import Collaboration
from app.models.message import Message
from app.models.researcher import ResearcherProfile
from app.models.user import User
from app.repositories import collaboration_repository, message_repository as repo
from app.schemas.message import MessageCreate, MessageOut, MessageListResponse, UnreadMessageCountOut
from app.utils.notifications import notify

router = APIRouter(tags=["Messages"])


def _require_my_profile(db: Session, current_user: User) -> ResearcherProfile:
    profile = db.scalar(select(ResearcherProfile).where(ResearcherProfile.user_id == current_user.user_id))
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You need a researcher profile before messaging",
        )
    return profile


def _require_participant(db: Session, collaboration_id: int, me: ResearcherProfile) -> Collaboration:
    collaboration = collaboration_repository.get_by_id(db, collaboration_id)
    if collaboration is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collaboration not found")
    if me.researcher_id not in (collaboration.researcher1_id, collaboration.researcher2_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only message researchers you're already connected with",
        )
    return collaboration


def _message_out(message: Message) -> MessageOut:
    return MessageOut(
        message_id=message.message_id,
        collaboration_id=message.collaboration_id,
        sender_id=message.sender_id,
        sender_name=f"{message.sender.first_name} {message.sender.last_name}",
        body=message.body,
        is_read=message.is_read,
        created_at=message.created_at,
    )


@router.post(
    "/collaborations/{collaboration_id}/messages", response_model=MessageOut, status_code=status.HTTP_201_CREATED,
)
def send_message(
    collaboration_id: int,
    payload: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    me = _require_my_profile(db, current_user)
    collaboration = _require_participant(db, collaboration_id, me)

    message = Message(collaboration_id=collaboration_id, sender_id=me.researcher_id, body=payload.body)
    db.add(message)
    db.commit()
    db.refresh(message)
    message = repo.get_by_id(db, message.message_id)

    other_id = (
        collaboration.researcher2_id if collaboration.researcher1_id == me.researcher_id else collaboration.researcher1_id
    )
    other = db.get(ResearcherProfile, other_id)
    if other is not None and other.user_id != current_user.user_id:
        notify(
            db, other.user_id, "message_received", f"New message from {me.first_name} {me.last_name}",
            payload.body[:140],
            link_url=f"/collaborations/{collaboration_id}",
        )
    return _message_out(message)


@router.get("/collaborations/{collaboration_id}/messages", response_model=MessageListResponse)
def list_messages(
    collaboration_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    me = _require_my_profile(db, current_user)
    _require_participant(db, collaboration_id, me)

    messages = repo.list_thread(db, collaboration_id)
    repo.mark_thread_read(db, collaboration_id, reader_researcher_id=me.researcher_id)

    return MessageListResponse(items=[_message_out(m) for m in messages], total=len(messages))


@router.get("/messages/unread-count", response_model=UnreadMessageCountOut)
def unread_message_count(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    me = _require_my_profile(db, current_user)
    return UnreadMessageCountOut(unread_count=repo.unread_count(db, me.researcher_id))