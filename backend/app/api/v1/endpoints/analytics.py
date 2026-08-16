from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories import analytics_repository as repo
from app.schemas.analytics import (
    TopPaperOut, InfluentialPaperOut, TopResearcherOut, TopInstitutionOut, CitationAnalyticsOut,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/citations/top-papers", response_model=list[TopPaperOut])
def top_papers(
    limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    return [
        TopPaperOut(publication_id=p.publication_id, title=p.title, citation_count=count)
        for p, count in repo.top_papers(db, limit)
    ]


@router.get("/citations/influential-papers", response_model=list[InfluentialPaperOut])
def influential_papers(
    limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    return [
        InfluentialPaperOut(publication_id=p.publication_id, title=p.title, influence_score=score)
        for p, score in repo.influential_papers(db, limit)
    ]


@router.get("/citations/top-researchers", response_model=list[TopResearcherOut])
def top_researchers(
    limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    return [
        TopResearcherOut(
            researcher_id=r.researcher_id, name=f"{r.first_name} {r.last_name}",
            total_citations=total, publication_count=pub_count,
        )
        for r, total, pub_count in repo.top_researchers(db, limit)
    ]


@router.get("/citations/top-institutions", response_model=list[TopInstitutionOut])
def top_institutions(
    limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    return [
        TopInstitutionOut(
            institution_id=i.institution_id, name=i.name,
            total_citations=total, publication_count=pub_count,
            avg_citations_per_publication=round(total / pub_count, 2) if pub_count else 0.0,
        )
        for i, total, pub_count in repo.top_institutions(db, limit)
    ]


@router.get("", response_model=CitationAnalyticsOut)
def citation_analytics(
    limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    return CitationAnalyticsOut(
        top_papers=[TopPaperOut(publication_id=p.publication_id, title=p.title, citation_count=c) for p, c in repo.top_papers(db, limit)],
        influential_papers=[
            InfluentialPaperOut(publication_id=p.publication_id, title=p.title, influence_score=s)
            for p, s in repo.influential_papers(db, limit)
        ],
        top_researchers=[
            TopResearcherOut(researcher_id=r.researcher_id, name=f"{r.first_name} {r.last_name}", total_citations=t, publication_count=pc)
            for r, t, pc in repo.top_researchers(db, limit)
        ],
        top_institutions=[
            TopInstitutionOut(
                institution_id=i.institution_id, name=i.name, total_citations=t, publication_count=pc,
                avg_citations_per_publication=round(t / pc, 2) if pc else 0.0,
            )
            for i, t, pc in repo.top_institutions(db, limit)
        ],
    )