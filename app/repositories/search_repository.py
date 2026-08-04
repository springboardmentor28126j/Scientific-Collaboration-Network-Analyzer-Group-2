from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.researcher import Researcher
from app.models.publication import Publication
from app.models.institution import Institution
from app.models.department import Department


class SearchRepository:

    @staticmethod
    def search_researchers(
        db: Session,
        query: str,
        page: int,
        page_size: int,
        institution: str = None,
        sort: str = "relevance",
    ):
        q = (
            db.query(Researcher)
            .filter(
                or_(
                    (Researcher.first_name + " " + Researcher.last_name).ilike(f"%{query}%"),
                    Researcher.bio.ilike(f"%{query}%"),
                    Researcher.orcid.ilike(f"%{query}%"),
                )
            )
        )

        if institution:
            q = (
                q.join(Researcher.departments)
                .join(Department.institution)
                .filter(Institution.name.ilike(f"%{institution}%"))
            )

        if sort == "oldest":
            q = q.order_by(Researcher.first_name.asc())
        else:
            q = q.order_by(Researcher.last_name.asc())

        total = q.count()

        data = (
            q.offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return total, data

    @staticmethod
    def search_publications(
        db: Session,
        query: str,
        page: int,
        page_size: int,
        year: int = None,
        publication_type: str = None,
        status: str = None,
        sort: str = "relevance",
    ):
        q = (
            db.query(Publication)
            .filter(
                or_(
                    Publication.title.ilike(f"%{query}%"),
                    Publication.abstract.ilike(f"%{query}%"),
                    Publication.doi.ilike(f"%{query}%"),
                    Publication.journal.ilike(f"%{query}%"),
                    Publication.conference.ilike(f"%{query}%"),
                )
            )
        )

        # -----------------------------
        # Filters
        # -----------------------------

        if year:
            q = q.filter(
                Publication.publication_year == year
            )

        if publication_type:
            q = q.filter(
                Publication.publication_type == publication_type
            )

        if status:
            q = q.filter(
                Publication.status == status
            )

        # -----------------------------
        # Sorting
        # -----------------------------

        if sort == "newest":
            q = q.order_by(
                Publication.publication_year.desc()
            )

        elif sort == "oldest":
            q = q.order_by(
                Publication.publication_year.asc()
            )

        elif sort == "citations":
            q = q.order_by(
                Publication.citation_count.desc()
            )

        else:
            q = q.order_by(
                Publication.publication_year.desc()
            )

        total = q.count()

        data = (
            q.offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return total, data

    @staticmethod
    def search_institutions(
        db: Session,
        query: str,
        page: int,
        page_size: int,
        sort: str = "relevance",
    ):
        q = (
            db.query(Institution)
            .filter(
                or_(
                    Institution.name.ilike(f"%{query}%"),
                    Institution.city.ilike(f"%{query}%"),
                    Institution.state.ilike(f"%{query}%"),
                    Institution.country.ilike(f"%{query}%"),
                )
            )
        )

        if sort == "oldest":
            q = q.order_by(Institution.name.asc())
        else:
            q = q.order_by(Institution.name.asc())

        total = q.count()

        data = (
            q.offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return total, data
