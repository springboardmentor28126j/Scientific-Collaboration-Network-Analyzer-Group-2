from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.routes.notifications import create_notification
from app.core.email import send_email
from app.db.session import get_db
from app.models.collaboration import Collaboration
from app.models.message import Conversation, ConversationRead, Message
from app.models.project import Project, ProjectMember, ProjectMemberStatus
from app.models.researcher import Researcher
from app.models.user import User
from app.schemas.message import ConversationOut, ConversationSummary, InboxOut, MessageCreate, MessageOut

router = APIRouter()


def _current_researcher(db: Session, current_user: User) -> Researcher:
    researcher = db.query(Researcher).filter(Researcher.user_id == current_user.id).first()
    if researcher is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only researchers have messages.")
    return researcher


def _project_participant_ids(db: Session, project: Project) -> list[int]:
    ids = {m.researcher_id for m in project.members if m.status == ProjectMemberStatus.ACCEPTED}
    ids.add(project.lead_researcher_id)
    return list(ids)


def _get_or_create_project_conversation(db: Session, project_id: int, researcher: Researcher) -> Conversation:
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if researcher.id not in _project_participant_ids(db, project):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You're not a member of this project.")

    conversation = db.query(Conversation).filter(Conversation.project_id == project_id).first()
    if conversation is None:
        conversation = Conversation(project_id=project_id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    return conversation


def _get_or_create_collaboration_conversation(
    db: Session, collaboration_id: int, researcher: Researcher
) -> Conversation:
    collaboration = db.query(Collaboration).filter(Collaboration.id == collaboration_id).first()
    if collaboration is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collaboration not found")
    if researcher.id not in (collaboration.researcher1_id, collaboration.researcher2_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You're not part of this collaboration.")

    conversation = db.query(Conversation).filter(Conversation.collaboration_id == collaboration_id).first()
    if conversation is None:
        conversation = Conversation(collaboration_id=collaboration_id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    return conversation


def _participant_ids(db: Session, conversation: Conversation) -> list[int]:
    if conversation.project_id:
        return _project_participant_ids(db, conversation.project)
    return [conversation.collaboration.researcher1_id, conversation.collaboration.researcher2_id]


def _scope_label(conversation: Conversation) -> tuple[str, int, str]:
    if conversation.project_id:
        return "project", conversation.project_id, conversation.project.title
    partner_pair = f"Researcher #{conversation.collaboration.researcher1_id} & #{conversation.collaboration.researcher2_id}"
    return "collaboration", conversation.collaboration_id, partner_pair


def _mark_read(db: Session, conversation_id: int, researcher_id: int) -> None:
    read = (
        db.query(ConversationRead)
        .filter(ConversationRead.conversation_id == conversation_id, ConversationRead.researcher_id == researcher_id)
        .first()
    )
    if read is None:
        read = ConversationRead(conversation_id=conversation_id, researcher_id=researcher_id)
        db.add(read)
    read.last_read_at = datetime.utcnow()
    db.commit()


def _to_conversation_out(conversation: Conversation, current_researcher_id: int) -> ConversationOut:
    scope_type, scope_id, scope_label = _scope_label(conversation)
    return ConversationOut(
        id=conversation.id,
        scope_type=scope_type,
        scope_id=scope_id,
        scope_label=scope_label,
        messages=[
            MessageOut(
                id=m.id,
                body=m.body,
                created_at=m.created_at,
                sender_researcher_id=m.sender_researcher_id,
                sender_email=m.sender.user.email,
                is_mine=m.sender_researcher_id == current_researcher_id,
            )
            for m in conversation.messages
        ],
    )


def _send_message(db: Session, conversation: Conversation, sender: Researcher, body: str) -> Message:
    message = Message(conversation_id=conversation.id, sender_researcher_id=sender.id, body=body)
    db.add(message)
    db.commit()
    db.refresh(message)

    scope_type, scope_id, scope_label = _scope_label(conversation)
    link = f"/{'projects' if scope_type == 'project' else 'collaborations'}/{scope_id}/messages"

    for participant_id in _participant_ids(db, conversation):
        if participant_id == sender.id:
            continue
        recipient = db.query(Researcher).filter(Researcher.id == participant_id).first()
        if recipient is None:
            continue
        create_notification(
            db,
            recipient_user_id=recipient.user_id,
            type="new_message",
            message=f"New message in {scope_label} from {sender.user.email}",
            link=link,
        )
        send_email(
            to_email=recipient.user.email,
            subject=f"New message in {scope_label}",
            html_body=f"""
                <p><strong>{sender.user.email}</strong> sent a new message in <strong>{scope_label}</strong>:</p>
                <p style="padding:12px; background:#f5f5f5; border-radius:6px;">{body}</p>
                <p><a href="{link}">Open the conversation</a></p>
            """,
        )

    return message


@router.get("/project/{project_id}", response_model=ConversationOut)
def get_project_conversation(
    project_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> ConversationOut:
    researcher = _current_researcher(db, current_user)
    conversation = _get_or_create_project_conversation(db, project_id, researcher)
    _mark_read(db, conversation.id, researcher.id)
    return _to_conversation_out(conversation, researcher.id)


@router.post("/project/{project_id}", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
def send_project_message(
    project_id: int,
    payload: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageOut:
    researcher = _current_researcher(db, current_user)
    conversation = _get_or_create_project_conversation(db, project_id, researcher)
    message = _send_message(db, conversation, researcher, payload.body)
    _mark_read(db, conversation.id, researcher.id)
    return MessageOut(
        id=message.id,
        body=message.body,
        created_at=message.created_at,
        sender_researcher_id=researcher.id,
        sender_email=current_user.email,
        is_mine=True,
    )


@router.get("/collaboration/{collaboration_id}", response_model=ConversationOut)
def get_collaboration_conversation(
    collaboration_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> ConversationOut:
    researcher = _current_researcher(db, current_user)
    conversation = _get_or_create_collaboration_conversation(db, collaboration_id, researcher)
    _mark_read(db, conversation.id, researcher.id)
    return _to_conversation_out(conversation, researcher.id)


@router.post("/collaboration/{collaboration_id}", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
def send_collaboration_message(
    collaboration_id: int,
    payload: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageOut:
    researcher = _current_researcher(db, current_user)
    conversation = _get_or_create_collaboration_conversation(db, collaboration_id, researcher)
    message = _send_message(db, conversation, researcher, payload.body)
    _mark_read(db, conversation.id, researcher.id)
    return MessageOut(
        id=message.id,
        body=message.body,
        created_at=message.created_at,
        sender_researcher_id=researcher.id,
        sender_email=current_user.email,
        is_mine=True,
    )


@router.get("/inbox", response_model=InboxOut)
def inbox(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> InboxOut:
    researcher = _current_researcher(db, current_user)

    project_ids = [
        m.project_id
        for m in db.query(ProjectMember)
        .filter(ProjectMember.researcher_id == researcher.id, ProjectMember.status == ProjectMemberStatus.ACCEPTED)
        .all()
    ]
    led_project_ids = [p.id for p in db.query(Project).filter(Project.lead_researcher_id == researcher.id).all()]
    project_ids = list(set(project_ids + led_project_ids))

    collaboration_ids = [
        c.id
        for c in db.query(Collaboration)
        .filter(or_(Collaboration.researcher1_id == researcher.id, Collaboration.researcher2_id == researcher.id))
        .all()
    ]

    conversations = (
        db.query(Conversation)
        .filter(
            or_(
                Conversation.project_id.in_(project_ids) if project_ids else False,
                Conversation.collaboration_id.in_(collaboration_ids) if collaboration_ids else False,
            )
        )
        .all()
    )

    items = []
    for conversation in conversations:
        if not conversation.messages:
            continue
        scope_type, scope_id, scope_label = _scope_label(conversation)
        last_message = conversation.messages[-1]

        read = (
            db.query(ConversationRead)
            .filter(
                ConversationRead.conversation_id == conversation.id, ConversationRead.researcher_id == researcher.id
            )
            .first()
        )
        last_read_at = read.last_read_at if read else datetime.min
        unread_count = sum(
            1 for m in conversation.messages if m.created_at > last_read_at and m.sender_researcher_id != researcher.id
        )

        items.append(
            ConversationSummary(
                conversation_id=conversation.id,
                scope_type=scope_type,
                scope_id=scope_id,
                scope_label=scope_label,
                last_message_preview=last_message.body[:120],
                last_message_at=last_message.created_at,
                unread_count=unread_count,
            )
        )

    items.sort(key=lambda i: i.last_message_at or datetime.min, reverse=True)
    return InboxOut(items=items)