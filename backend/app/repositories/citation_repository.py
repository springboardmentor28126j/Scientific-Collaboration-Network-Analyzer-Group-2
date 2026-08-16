import re

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.citation import Citation
from app.models.publication import Publication


def get_by_id(db: Session, citation_id: int) -> Citation | None:
    stmt = (
        select(Citation)
        .where(Citation.citation_id == citation_id)
        .options(
            selectinload(Citation.citing_publication),
            selectinload(Citation.cited_publication),
            selectinload(Citation.added_by),
        )
    )
    return db.scalar(stmt)


def list_references(db: Session, citing_publication_id: int) -> list[Citation]:
    stmt = (
        select(Citation)
        .where(Citation.citing_publication_id == citing_publication_id)
        .options(selectinload(Citation.cited_publication), selectinload(Citation.added_by))
        .order_by(Citation.created_at.asc())
    )
    return list(db.scalars(stmt).all())


def list_cited_by(db: Session, cited_publication_id: int) -> list[Citation]:
    stmt = (
        select(Citation)
        .where(Citation.cited_publication_id == cited_publication_id)
        .options(selectinload(Citation.citing_publication), selectinload(Citation.added_by))
        .order_by(Citation.created_at.desc())
    )
    return list(db.scalars(stmt).all())


def citation_count(db: Session, publication_id: int) -> int:
    stmt = select(Citation).where(Citation.cited_publication_id == publication_id)
    return len(list(db.scalars(stmt).all()))


def author_list(publication: Publication) -> list[tuple[str, str]]:
    ordered = [publication.primary_author] + [
        ca.researcher for ca in sorted(publication.co_authors, key=lambda ca: ca.author_order)
        if ca.researcher_id != publication.primary_author_id
    ]
    return [(a.first_name, a.last_name) for a in ordered if a is not None]


def _year(publication: Publication) -> str:
    return str(publication.publication_date.year) if publication.publication_date else "n.d."


def format_apa(publication: Publication) -> str:
    authors = author_list(publication)
    author_str = ", ".join(f"{last}, {first[0]}." for first, last in authors) if authors else "Unknown author"
    parts = [f"{author_str} ({_year(publication)}). {publication.title}."]
    if publication.venue_name:
        parts.append(f" {publication.venue_name}.")
    if publication.doi:
        parts.append(f" https://doi.org/{publication.doi}" if not publication.doi.startswith("http") else f" {publication.doi}")
    return "".join(parts)


def format_mla(publication: Publication) -> str:
    authors = author_list(publication)
    if authors:
        first, last = authors[0]
        author_str = f"{last}, {first}" + (", et al." if len(authors) > 1 else ".")
    else:
        author_str = "Unknown author."
    parts = [f'{author_str} "{publication.title}."']
    if publication.venue_name:
        parts.append(f" {publication.venue_name},")
    parts.append(f" {_year(publication)}.")
    if publication.doi:
        parts.append(f" doi:{publication.doi}." if not publication.doi.startswith("http") else f" {publication.doi}.")
    return " ".join(p.strip() for p in parts).strip()


def format_bibtex(publication: Publication) -> str:
    authors = author_list(publication)
    author_str = " and ".join(f"{last}, {first}" for first, last in authors) if authors else "Unknown author"

    key_source = (authors[0][1] if authors else "unknown") + _year(publication)
    key = re.sub(r"[^a-zA-Z0-9]", "", key_source).lower() or f"pub{publication.publication_id}"

    entry_type = "article" if publication.publication_type.value in ("journal_paper", "conference_paper") else "misc"

    fields = [f'  author = {{{author_str}}}', f'  title = {{{publication.title}}}', f'  year = {{{_year(publication)}}}']
    if publication.venue_name:
        field_name = "journal" if publication.publication_type.value == "journal_paper" else "booktitle"
        fields.append(f'  {field_name} = {{{publication.venue_name}}}')
    if publication.doi:
        fields.append(f'  doi = {{{publication.doi}}}')

    return f"@{entry_type}{{{key},\n" + ",\n".join(fields) + "\n}"