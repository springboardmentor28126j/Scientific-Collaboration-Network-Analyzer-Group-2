from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.citation import Citation
from app.models.publication import Publication
from app.models.researcher import ResearcherProfile
from app.models.user import User, UserRole
from app.repositories import citation_repository as repo
from app.schemas.citation import CitationCreate, CitationOut, CitationListResponse, CitationTextOut
from app.utils.audit import write_audit_log
from app.utils.notifications import notify

router = APIRouter(tags=["Citations"])


def _get_publication_or_404(db: Session, publication_id: int) -> Publication:
    publication = db.get(Publication, publication_id)
    if publication is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")
    return publication


def _citation_out(citation: Citation) -> CitationOut:
    if citation.is_internal:
        cited = citation.cited_publication
        display_title = cited.title if cited else "(publication removed)"
        display_authors = None
        if cited is not None:
            names = repo.author_list(cited)
            display_authors = ", ".join(f"{f} {l}" for f, l in names) or None
        display_venue = cited.venue_name if cited else None
        display_year = cited.publication_date.year if cited and cited.publication_date else None
        display_doi = cited.doi if cited else None
    else:
        display_title = citation.external_title
        display_authors = citation.external_authors
        display_venue = citation.external_venue
        display_year = citation.external_year
        display_doi = citation.external_doi

    return CitationOut(
        citation_id=citation.citation_id,
        citing_publication_id=citation.citing_publication_id,
        citing_publication_title=citation.citing_publication.title,
        cited_publication_id=citation.cited_publication_id,
        is_internal=citation.is_internal,
        display_title=display_title,
        display_authors=display_authors,
        display_venue=display_venue,
        display_year=display_year,
        display_doi=display_doi,
        context=citation.context,
        added_by_researcher_id=citation.added_by_id,
        added_by_name=f"{citation.added_by.first_name} {citation.added_by.last_name}",
        created_at=citation.created_at,
    )


@router.post(
    "/publications/{publication_id}/citations", response_model=CitationOut, status_code=status.HTTP_201_CREATED,
)
def add_citation(
    publication_id: int,
    payload: CitationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    citing_publication = _get_publication_or_404(db, publication_id)

    profile = db.scalar(select(ResearcherProfile).where(ResearcherProfile.user_id == current_user.user_id))
    is_owner = profile is not None and citing_publication.primary_author_id == profile.researcher_id
    if not is_owner and current_user.role != UserRole.SYSTEM_ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the primary author can add citations to this publication")
    if profile is None:
        # Permission passed -- must be a system admin, since is_owner
        # requires a profile -- but added_by_id is real provenance (who is
        # vouching for this reference), not just an audit stamp, so it
        # can't be defaulted to anyone. This is a different problem than
        # the 403 above and deserves a different message.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="System admin accounts need a researcher profile to be recorded as who added a citation",
        )
    me = profile

    cited_publication = None
    if payload.cited_publication_id is not None:
        if payload.cited_publication_id == publication_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A publication can't cite itself")
        cited_publication = _get_publication_or_404(db, payload.cited_publication_id)

        existing = db.scalar(
            select(Citation).where(
                Citation.citing_publication_id == publication_id,
                Citation.cited_publication_id == payload.cited_publication_id,
            )
        )
        if existing is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This publication already cites that one")

    citation = Citation(
        citing_publication_id=publication_id,
        cited_publication_id=payload.cited_publication_id,
        external_title=payload.external_title,
        external_authors=payload.external_authors,
        external_venue=payload.external_venue,
        external_year=payload.external_year,
        external_doi=payload.external_doi,
        context=payload.context,
        added_by_id=me.researcher_id,
    )
    db.add(citation)
    db.commit()
    db.refresh(citation)
    citation = repo.get_by_id(db, citation.citation_id)

    write_audit_log(db, current_user.user_id, "CREATE", "citation", citation.citation_id)

    if cited_publication is not None and cited_publication.primary_author.user_id != current_user.user_id:
        notify(
            db, cited_publication.primary_author.user_id, "citation_received", "Your work was cited",
            f'"{citing_publication.title}" cited your publication "{cited_publication.title}".',
            link_url=f"/publications/{cited_publication.publication_id}",
        )
    return _citation_out(citation)


@router.get("/publications/{publication_id}/citations", response_model=CitationListResponse)
def list_references(
    publication_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    _get_publication_or_404(db, publication_id)
    items = [_citation_out(c) for c in repo.list_references(db, publication_id)]
    return CitationListResponse(items=items, total=len(items))


@router.get("/publications/{publication_id}/cited-by", response_model=CitationListResponse)
def list_cited_by(
    publication_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    _get_publication_or_404(db, publication_id)
    items = [_citation_out(c) for c in repo.list_cited_by(db, publication_id)]
    return CitationListResponse(items=items, total=len(items))


@router.get("/publications/{publication_id}/citation-text", response_model=CitationTextOut)
def get_citation_text(
    publication_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    publication = _get_publication_or_404(db, publication_id)
    return CitationTextOut(
        apa=repo.format_apa(publication),
        mla=repo.format_mla(publication),
        bibtex=repo.format_bibtex(publication),
    )


@router.delete("/citations/{citation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_citation(
    citation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    citation = repo.get_by_id(db, citation_id)
    if citation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Citation not found")

    profile = db.scalar(select(ResearcherProfile).where(ResearcherProfile.user_id == current_user.user_id))
    is_owner = profile is not None and (
        citation.added_by_id == profile.researcher_id or citation.citing_publication.primary_author_id == profile.researcher_id
    )
    if not is_owner and current_user.role != UserRole.SYSTEM_ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to remove this citation")

    write_audit_log(db, current_user.user_id, "DELETE", "citation", citation_id)
    db.delete(citation)
    db.commit()