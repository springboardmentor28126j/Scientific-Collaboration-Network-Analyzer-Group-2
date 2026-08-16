from sqlalchemy import select, func, desc
from sqlalchemy.orm import Session

from app.models.citation import Citation
from app.models.institution import Institution
from app.models.publication import Publication, PublicationAuthor
from app.models.researcher import ResearcherProfile


def _cited_counts_subquery():
    """publication_id -> how many citations it has received. Reused by
    every query below instead of each one re-deriving it, since 'how many
    times has X been cited' is the atomic fact all four questions build on."""
    return (
        select(Citation.cited_publication_id.label("publication_id"), func.count(Citation.citation_id).label("cnt"))
        .where(Citation.cited_publication_id.isnot(None))
        .group_by(Citation.cited_publication_id)
        .subquery()
    )


def top_papers(db: Session, limit: int = 10) -> list[tuple[Publication, int]]:
    """'Frequently referenced' -- raw incoming citation count, most cited first."""
    counts = _cited_counts_subquery()
    stmt = (
        select(Publication, counts.c.cnt)
        .join(counts, counts.c.publication_id == Publication.publication_id)
        .order_by(desc(counts.c.cnt))
        .limit(limit)
    )
    return [(row[0], row[1]) for row in db.execute(stmt).all()]


def influential_papers(db: Session, limit: int = 10) -> list[tuple[Publication, int]]:
    """
    'Most influential' -- a citation from a paper that is itself
    highly-cited counts more than one from an uncited paper. One-hop
    weighted score: score(P) = sum over each citation P receives of
    (1 + citation_count of the paper doing the citing). Deliberately not
    full iterative PageRank -- a single-pass weighted sum is explainable
    and cheap to compute live, whereas PageRank's fixed-point iteration
    would need to run as a batch job to stay fast, which isn't justified
    at this data scale.
    """
    counts = _cited_counts_subquery()
    stmt = (
        select(
            Publication,
            func.sum(1 + func.coalesce(counts.c.cnt, 0)).label("influence_score"),
        )
        .join(Citation, Citation.cited_publication_id == Publication.publication_id)
        .outerjoin(counts, counts.c.publication_id == Citation.citing_publication_id)
        .group_by(Publication.publication_id)
        .order_by(desc("influence_score"))
        .limit(limit)
    )
    return [(row[0], int(row[1])) for row in db.execute(stmt).all()]


def top_researchers(db: Session, limit: int = 10) -> list[tuple[ResearcherProfile, int, int]]:
    """Most cited researcher -- sum of citations across every publication
    where they're primary author OR a listed co-author."""
    primary_link = select(Publication.publication_id, Publication.primary_author_id.label("researcher_id"))
    coauthor_link = select(PublicationAuthor.publication_id, PublicationAuthor.researcher_id)
    author_pub = primary_link.union_all(coauthor_link).subquery()

    counts = _cited_counts_subquery()

    stmt = (
        select(
            author_pub.c.researcher_id,
            func.coalesce(func.sum(counts.c.cnt), 0).label("total_citations"),
            func.count(func.distinct(author_pub.c.publication_id)).label("publication_count"),
        )
        .outerjoin(counts, counts.c.publication_id == author_pub.c.publication_id)
        .group_by(author_pub.c.researcher_id)
        .order_by(desc("total_citations"))
        .limit(limit)
    )
    rows = db.execute(stmt).all()

    researcher_ids = [r.researcher_id for r in rows]
    if not researcher_ids:
        return []
    researchers = {
        r.researcher_id: r for r in db.scalars(select(ResearcherProfile).where(ResearcherProfile.researcher_id.in_(researcher_ids)))
    }
    return [
        (researchers[r.researcher_id], int(r.total_citations), int(r.publication_count))
        for r in rows if r.researcher_id in researchers
    ]


def top_institutions(db: Session, limit: int = 10) -> list[tuple[Institution, int, int]]:
    """Institution with the highest research impact. Returns both raw
    total citations and publication count -- average-per-publication is
    exposed too so a small institution with a few highly-cited papers
    doesn't get buried under one that just publishes more volume."""
    counts = _cited_counts_subquery()
    stmt = (
        select(
            Publication.institution_id,
            func.coalesce(func.sum(counts.c.cnt), 0).label("total_citations"),
            func.count(func.distinct(Publication.publication_id)).label("publication_count"),
        )
        .outerjoin(counts, counts.c.publication_id == Publication.publication_id)
        .where(Publication.institution_id.isnot(None))
        .group_by(Publication.institution_id)
        .order_by(desc("total_citations"))
        .limit(limit)
    )
    rows = db.execute(stmt).all()

    institution_ids = [r.institution_id for r in rows]
    if not institution_ids:
        return []
    institutions = {
        i.institution_id: i for i in db.scalars(select(Institution).where(Institution.institution_id.in_(institution_ids)))
    }
    return [
        (institutions[r.institution_id], int(r.total_citations), int(r.publication_count))
        for r in rows if r.institution_id in institutions
    ]