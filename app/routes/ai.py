from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app import models
from app.ai_assistant import keyword_suggestions, paper_score, profile_score
from app.database import get_db
from app.permissions import current_user, is_system_admin, scoped_publications_query, scoped_researchers_query

router = APIRouter(prefix="/ai", tags=["AI-assisted discovery"])


class KeywordRequest(BaseModel):
    title: str = Field(default="", max_length=500)
    abstract: str = Field(default="", max_length=10000)


@router.get("/paper-recommendations")
def recommend_papers(query: str = Query(min_length=1, max_length=500), limit: int = Query(default=8, ge=1, le=20), user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    results = []
    for publication in scoped_publications_query(db, user).all():
        score, matched_terms = paper_score(query, publication.title, publication.abstract)
        if score:
            results.append({"id": publication.id, "title": publication.title, "abstract": publication.abstract, "relevance_score": score, "matched_terms": matched_terms, "publication_type": publication.publication_type, "status": publication.status, "authors": [author.full_name for author in publication.authors]})
    return {"query": query, "method": "Local explainable keyword matching", "results": sorted(results, key=lambda item: item["relevance_score"], reverse=True)[:limit]}


@router.post("/keyword-suggestions")
def suggest_keywords(payload: KeywordRequest, _user: models.User = Depends(current_user)):
    return {"keywords": keyword_suggestions(payload.title, payload.abstract), "method": "Local term-frequency extraction"}


@router.get("/collaborator-recommendations")
def recommend_collaborators(researcher_id: int | None = None, limit: int = Query(default=8, ge=1, le=20), user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    source_id = researcher_id or user.researcher_id
    if not source_id:
        raise HTTPException(status_code=400, detail="Choose a researcher profile to receive collaborator recommendations")
    source = scoped_researchers_query(db, user).filter(models.Researcher.id == source_id).first()
    if not source and is_system_admin(user):
        source = db.query(models.Researcher).filter(models.Researcher.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Researcher profile is outside your permitted workspace")
    connected_ids = set()
    for item in db.query(models.Collaboration).filter((models.Collaboration.researcher1_id == source.id) | (models.Collaboration.researcher2_id == source.id)).all():
        connected_ids.add(item.researcher2_id if item.researcher1_id == source.id else item.researcher1_id)
    results = []
    # Researcher profiles are discoverable for collaboration suggestions; the
    # returned card deliberately contains academic information only, not user
    # account data. Other modules keep their normal workspace restrictions.
    candidate_query = db.query(models.Researcher) if user.role.lower() == "researcher" else scoped_researchers_query(db, user)
    for candidate in candidate_query.filter(models.Researcher.id != source.id).all():
        if candidate.id in connected_ids:
            continue
        score, shared = profile_score(source, candidate)
        if score:
            results.append({"id": candidate.id, "full_name": candidate.full_name, "department": candidate.department, "designation": candidate.designation, "institution": candidate.institution.name if candidate.institution else "Not assigned", "match_score": score, "shared_topics": shared})
    return {"researcher": {"id": source.id, "full_name": source.full_name}, "method": "Shared skills, interests and institution", "results": sorted(results, key=lambda item: item["match_score"], reverse=True)[:limit]}
