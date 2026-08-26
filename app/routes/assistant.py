"""Local LLM assistant grounded in the logged-in user's live SCNA records."""
import json
import os
from urllib.error import URLError
from urllib.request import Request, urlopen

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.permissions import current_user, is_system_admin, scoped_collaborations_query, scoped_projects_query, scoped_publications_query

router = APIRouter(prefix="/assistant", tags=["SCNA Assistant"])
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")


class ChatMessage(BaseModel):
    message: str = Field(min_length=1, max_length=500)


def _records_context(user: models.User, db: Session, question: str) -> str:
    """Build concise context containing only records permitted for this role."""
    publications = scoped_publications_query(db, user).order_by(models.Publication.created_at.desc()).limit(20).all()
    publication_lines = [f"- {item.title} | {item.status} | {item.publication_type} | abstract: {(item.abstract or 'not provided')[:240]}" for item in publications]

    projects = [] if user.role.lower() == "reviewer" else scoped_projects_query(db, user).limit(15).all()
    project_lines = [f"- {item.title} | {item.status} | funding: {item.funding_agency or 'not provided'}" for item in projects]

    collaborations = [] if user.role.lower() == "reviewer" else scoped_collaborations_query(db, user).limit(20).all()
    collaboration_lines = [f"- {item.researcher1.full_name} with {item.researcher2.full_name} | {item.status} | project: {item.project or 'not provided'}" for item in collaborations]

    review_lines = []
    if user.role.lower() == "reviewer":
        reviews = db.query(models.ReviewAssignment).filter(models.ReviewAssignment.reviewer_id == user.id).all()
        review_lines = [f"- {item.publication.title} | {item.status} | due: {item.due_date or 'not set'}" for item in reviews]
    elif user.role.lower() == "institution admin" and user.institution_id:
        reviews = db.query(models.ReviewAssignment).join(models.Publication).filter(models.Publication.institution_id == user.institution_id).all()
        review_lines = [f"- {item.publication.title} | {item.status} | due: {item.due_date or 'not set'}" for item in reviews]
    elif is_system_admin(user) or user.role.lower() == "publisher":
        reviews = db.query(models.ReviewAssignment).limit(20).all()
        review_lines = [f"- {item.publication.title} | {item.status} | due: {item.due_date or 'not set'}" for item in reviews]

    admin_summary = ""
    if is_system_admin(user):
        institution_rows = db.query(models.Institution.name, func.count(models.Publication.id)).outerjoin(models.Publication).group_by(models.Institution.id, models.Institution.name).order_by(func.count(models.Publication.id).desc()).limit(8).all()
        admin_summary = f"\nADMIN SUMMARY: total researchers={db.query(models.Researcher).count()}, total institutions={db.query(models.Institution).count()}, total publications={db.query(models.Publication).count()}, institution publication counts={[(name, count) for name, count in institution_rows]}"

    sections = {
        "publications": f"ACCESSIBLE PUBLICATIONS ({len(publication_lines)}):\n{chr(10).join(publication_lines) or '- none'}",
        "projects": f"ACCESSIBLE PROJECTS ({len(project_lines)}):\n{chr(10).join(project_lines) or '- none'}",
        "collaborations": f"ACCESSIBLE COLLABORATIONS ({len(collaboration_lines)}):\n{chr(10).join(collaboration_lines) or '- none'}",
        "reviews": f"ACCESSIBLE REVIEW ASSIGNMENTS ({len(review_lines)}):\n{chr(10).join(review_lines) or '- none'}",
    }
    lowered = question.lower()
    requested = []
    if "publication" in lowered or "paper" in lowered:
        requested.append("publications")
    if "project" in lowered:
        requested.append("projects")
    if "collaboration" in lowered or "collaborator" in lowered:
        requested.append("collaborations")
    if "review" in lowered:
        requested.append("reviews")
    selected = requested or list(sections)
    return f"CURRENT USER: {user.name}; role: {user.role}.\n" + "\n\n".join(sections[key] for key in dict.fromkeys(selected)) + admin_summary


def _ask_ollama(question: str, context: str) -> str:
    system_prompt = """You are SCNA Assistant, a helpful research-management chatbot. Answer only from the SCNA RECORDS supplied in the user message. Never invent names, counts, publications, actions, or permissions. For a request about titles, projects, collaborations, or reviews, copy the exact relevant names from the records. For a summary, mention exact counts and at least one exact record name when available. If data is absent, say that the available SCNA records do not contain the answer. Be concise and use plain language."""
    grounded_question = f"SCNA RECORDS (authoritative):\n{context}\n\nUSER QUESTION: {question}\n\nAnswer from SCNA RECORDS only."
    body = json.dumps({"model": OLLAMA_MODEL, "stream": False, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": grounded_question}], "options": {"temperature": 0, "num_predict": 260}}).encode()
    request = Request(f"{OLLAMA_URL}/api/chat", data=body, headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=90) as response:
            payload = json.loads(response.read().decode())
    except (URLError, TimeoutError, OSError) as error:
        raise HTTPException(status_code=503, detail="Local AI model is unavailable. Start Ollama and make sure the configured model is downloaded.") from error
    answer = (payload.get("message") or {}).get("content", "").strip()
    if not answer:
        raise HTTPException(status_code=503, detail="The local AI model did not return an answer. Please try again.")
    return answer


@router.get("/status")
def assistant_status():
    return {"provider": "Ollama local model", "model": OLLAMA_MODEL, "endpoint": OLLAMA_URL}


@router.post("/chat")
def chat(payload: ChatMessage, user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    question = payload.message.strip()
    answer = _ask_ollama(question, _records_context(user, db, question))
    return {"answer": answer, "suggestions": ["Summarize my research activity", "What publications do I have?", "What collaborations are pending?", "How do reports work?"], "source": f"Local Ollama ({OLLAMA_MODEL}) + live SCNA records"}
