from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.config import settings

router = APIRouter()


class AssistantChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    history: list[dict[str, str]] | None = None


class AssistantChatResponse(BaseModel):
    reply: str
    configured: bool
    results: list[dict[str, str]] = []


def _fallback_reply(message: str) -> str:
    text = (message or "").strip()
    if not text:
        return "Please enter a question to get a helpful answer."

    if "publication" in text.lower():
        return "To add a publication, open the Publications page from the main navigation and use the add form there."
    if "project" in text.lower():
        return "Open the Projects page from the navigation to create or review a research project."
    if "conference" in text.lower():
        return "Use the Conferences section to browse and register for academic events."
    if "report" in text.lower():
        return "Reports are available from the Reports menu, where you can review stats and export files."
    if "collab" in text.lower() or "collaboration" in text.lower():
        return "Visit Collaborations to send requests, review suggestions, and view collaboration activity."
    return "I can help you navigate SCNA. Try asking about publications, projects, conferences, reports, or collaborations."


@router.post("/chat", response_model=AssistantChatResponse)
async def chat(payload: AssistantChatRequest):
    history = payload.history or []
    user_message = payload.message.strip()

    if not settings.ANTHROPIC_API_KEY:
        return AssistantChatResponse(
            reply=_fallback_reply(user_message),
            configured=False,
            results=[
                {"title": "Publications", "url": "/publications", "subtitle": "Browse and manage publication records"},
                {"title": "Projects", "url": "/projects", "subtitle": "Track research initiatives and team members"},
                {"title": "Reports", "url": "/reports", "subtitle": "View platform analytics and exports"},
            ],
        )

    try:
        from anthropic import Anthropic
    except Exception:
        return AssistantChatResponse(
            reply="The AI assistant is configured, but the Anthropic SDK is not available in this environment. Please install backend dependencies and restart the service.",
            configured=True,
            results=[],
        )

    try:
        client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        prompt = "You are the SCNA in-app assistant. Keep answers short and grounded in the platform. User question: " + user_message
        if history:
            prompt += "\n\nRecent chat history:\n" + "\n".join(f"{h.get('role','user')}: {h.get('text', '')}" for h in history[-8:])

        completion = client.messages.create(
            model=settings.AI_MODEL,
            max_tokens=220,
            system="You help users navigate SCNA and answer questions about publications, projects, conferences, reports, and collaborations.",
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(block.text for block in completion.content if getattr(block, "type", None) == "text")
        if not text:
            text = "I’m here to help with SCNA navigation and discovery."
        return AssistantChatResponse(reply=text, configured=True, results=[])
    except Exception:
        return AssistantChatResponse(
            reply="The assistant is configured, but the model request failed. Please try again in a moment.",
            configured=True,
            results=[],
        )
