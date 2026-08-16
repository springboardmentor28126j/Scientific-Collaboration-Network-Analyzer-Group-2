from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.chatbot import ChatRequest, ChatResponse
from app.services import chatbot_service

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])


@router.post("/message", response_model=ChatResponse)
def send_message(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Sends the conversation so far (client-maintained history, oldest
    message first) and gets back the assistant's next reply. The assistant
    answers FAQ/navigation questions directly and answers questions about
    the current user's own platform data (publications, projects, reviews,
    collaborations, and institution/system stats for admins) by calling
    read-only tools scoped to that user's role -- see chatbot_service.py.
    """
    try:
        reply = chatbot_service.run_chat(db, current_user, [m.model_dump() for m in payload.messages])
    except chatbot_service.ChatbotUnavailable as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    return ChatResponse(reply=reply)
