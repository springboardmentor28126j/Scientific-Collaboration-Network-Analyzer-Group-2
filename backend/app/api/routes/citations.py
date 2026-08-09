from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.citation import Citation
from app.models.institution import Institution
from app.models.publication import Publication, PublicationAuthor
from app.models.researcher import Researcher
from app.models.user import User, UserRole
from app.schemas.citation import (
    CitationCreate,
    CitationNetworkEdge,
    CitationNetworkNode,
    CitationNetworkOut,
    CitationOut,
    TopAuthorOut,
    TopInstitutionOut,
    TopPaperOut,
)

router = APIRouter()


def _get_current_researcher(db: Session, current_user: User) -> Researcher:
    researcher = db.query(Researcher).filter(Researcher.user_id == current_user.id).first()
    if researcher is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Create a researcher profile before managing citations",
        )
    return researcher


def _get_publication_or_404(db: Session, publication_id: int) -> Publication:
    publication = (
        db.query(Publication)
        .options(selectinload(Publication.authors))
        .filter(Publication.id == publication_id)
        .first()
    )
    if publication is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found"
        )
    return publication


def _get_citation_or_404(db: Session, citation_id: int) -> Citation:
    citation = (
        db.query(Citation)
        .options(
            selectinload(Citation.citing_publication),
            selectinload(Citation.cited_publication),
        )
        .filter(Citation.id == citation_id)
        .first()
    )
    if citation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Citation not found")
    return citation


@router.post("", response_model=CitationOut, status_code=status.HTTP_201_CREATED)
def create_citation(
    payload: CitationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Citation:
    researcher = _get_current_researcher(db, current_user)
    citing_publication = _get_publication_or_404(db, payload.citing_publication_id)

    author_ids = {a.researcher_id for a in citing_publication.authors}
    if researcher.id not in author_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only an author of the citing publication can add a citation for it",
        )

    if payload.cited_publication_id is not None:
        _get_publication_or_404(db, payload.cited_publication_id)
        existing = (
            db.query(Citation)
            .filter(
                Citation.citing_publication_id == payload.citing_publication_id,
                Citation.cited_publication_id == payload.cited_publication_id,
            )
            .first()
        )
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This citation already exists",
            )

    citation = Citation(
        **payload.model_dump(),
        created_by_researcher_id=researcher.id,
    )
    db.add(citation)
    db.commit()
    db.refresh(citation)
    return _get_citation_or_404(db, citation.id)


@router.get("", response_model=list[CitationOut])
def list_citations(
    citing_publication_id: int | None = None,
    cited_publication_id: int | None = None,
    db: Session = Depends(get_db),
) -> list[Citation]:
    query = db.query(Citation).options(
        selectinload(Citation.citing_publication),
        selectinload(Citation.cited_publication),
    )
    if citing_publication_id is not None:
        query = query.filter(Citation.citing_publication_id == citing_publication_id)
    if cited_publication_id is not None:
        query = query.filter(Citation.cited_publication_id == cited_publication_id)
    return query.order_by(Citation.created_at.desc()).all()


@router.delete("/{citation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_citation(
    citation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    researcher = _get_current_researcher(db, current_user)
    citation = _get_citation_or_404(db, citation_id)

    if (
        citation.created_by_researcher_id != researcher.id
        and current_user.role != UserRole.SYSTEM_ADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the researcher who added this citation (or a System Admin) can delete it",
        )

    db.delete(citation)
    db.commit()


@router.get("/stats/top-papers", response_model=list[TopPaperOut])
def top_cited_papers(
    limit: int = 10,
    db: Session = Depends(get_db),
) -> list[TopPaperOut]:
    rows = (
        db.query(
            Publication.id.label("publication_id"),
            Publication.title,
            Publication.year,
            func.count(Citation.id).label("citation_count"),
        )
        .join(Citation, Citation.cited_publication_id == Publication.id)
        .group_by(Publication.id, Publication.title, Publication.year)
        .order_by(func.count(Citation.id).desc())
        .limit(limit)
        .all()
    )
    return [TopPaperOut.model_validate(row._mapping) for row in rows]


@router.get("/stats/top-authors", response_model=list[TopAuthorOut])
def top_cited_authors(
    limit: int = 10,
    db: Session = Depends(get_db),
) -> list[TopAuthorOut]:
    rows = (
        db.query(
            Researcher.id.label("researcher_id"),
            User.email,
            func.count(Citation.id).label("citation_count"),
        )
        .join(PublicationAuthor, PublicationAuthor.researcher_id == Researcher.id)
        .join(Citation, Citation.cited_publication_id == PublicationAuthor.publication_id)
        .join(User, User.id == Researcher.user_id)
        .group_by(Researcher.id, User.email)
        .order_by(func.count(Citation.id).desc())
        .limit(limit)
        .all()
    )
    return [TopAuthorOut.model_validate(row._mapping) for row in rows]


@router.get("/stats/top-institutions", response_model=list[TopInstitutionOut])
def top_cited_institutions(
    limit: int = 10,
    db: Session = Depends(get_db),
) -> list[TopInstitutionOut]:
    rows = (
        db.query(
            Institution.id.label("institution_id"),
            Institution.name,
            func.count(Citation.id).label("citation_count"),
        )
        .join(Researcher, Researcher.institution_id == Institution.id)
        .join(PublicationAuthor, PublicationAuthor.researcher_id == Researcher.id)
        .join(Citation, Citation.cited_publication_id == PublicationAuthor.publication_id)
        .group_by(Institution.id, Institution.name)
        .order_by(func.count(Citation.id).desc())
        .limit(limit)
        .all()
    )
    return [TopInstitutionOut.model_validate(row._mapping) for row in rows]


@router.get("/network", response_model=CitationNetworkOut)
def citation_network(
    publication_id: int | None = None,
    db: Session = Depends(get_db),
) -> CitationNetworkOut:
    """Full citation graph, or (with publication_id) just the direct
    in/out neighborhood of one paper. External citations (no
    cited_publication_id) appear as their own leaf node, keyed by a
    negative id derived from the citation row so it can't collide with a
    real publication id."""
    query = db.query(Citation).options(
        selectinload(Citation.citing_publication).selectinload(Publication.authors),
        selectinload(Citation.cited_publication).selectinload(Publication.authors),
    )
    if publication_id is not None:
        query = query.filter(
            (Citation.citing_publication_id == publication_id)
            | (Citation.cited_publication_id == publication_id)
        )
    citations = query.all()

    nodes: dict[int, CitationNetworkNode] = {}

    def _add_publication_node(pub: Publication) -> None:
        if pub.id in nodes:
            return
        researcher_ids = [a.researcher_id for a in pub.authors]
        institution_id = None
        if pub.authors:
            first_researcher = (
                db.query(Researcher).filter(Researcher.id == pub.authors[0].researcher_id).first()
            )
            institution_id = first_researcher.institution_id if first_researcher else None
        nodes[pub.id] = CitationNetworkNode(
            id=pub.id,
            label=pub.title,
            year=pub.year,
            researcher_ids=researcher_ids,
            institution_id=institution_id,
        )

    edges: list[CitationNetworkEdge] = []
    for citation in citations:
        _add_publication_node(citation.citing_publication)
        if citation.cited_publication is not None:
            _add_publication_node(citation.cited_publication)
            target_id = citation.cited_publication.id
        else:
            external_id = -citation.id
            if external_id not in nodes:
                nodes[external_id] = CitationNetworkNode(
                    id=external_id,
                    label=citation.cited_title or "External paper",
                    year=citation.cited_year,
                    researcher_ids=[],
                    institution_id=None,
                )
            target_id = external_id
        edges.append(CitationNetworkEdge(source=citation.citing_publication_id, target=target_id))

    return CitationNetworkOut(nodes=list(nodes.values()), edges=edges)