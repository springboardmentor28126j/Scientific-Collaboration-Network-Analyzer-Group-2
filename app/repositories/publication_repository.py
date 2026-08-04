from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session

from app.models.publication import Publication


class PublicationRepository:

    @staticmethod
    def create(
        db: Session,
        publication: Publication,
    ) -> Publication:
        db.add(publication)
        db.commit()
        db.refresh(publication)
        return publication

    @staticmethod
    def get_by_id(
        db: Session,
        publication_id,
    ) -> Publication | None:
        return (
            db.query(Publication)
            .filter(Publication.id == publication_id)
            .first()
        )

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ):
        return (
            db.query(Publication)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_owner(
        db: Session,
        owner_id,
    ):
        return (
            db.query(Publication)
            .filter(Publication.owner_id == owner_id)
            .all()
        )

    @staticmethod
    def get_by_doi(
        db: Session,
        doi: str,
    ):
        return (
            db.query(Publication)
            .filter(Publication.doi == doi)
            .first()
        )

    @staticmethod
    def update(
        db: Session,
        publication: Publication,
    ) -> Publication:
        db.commit()
        db.refresh(publication)
        return publication

    @staticmethod
    def delete(
        db: Session,
        publication: Publication,
    ) -> None:
        db.delete(publication)
        db.commit()

    @staticmethod
    def search(
        db: Session,
        keyword: str,
    ):
        keyword = f"%{keyword}%"

        return (
            db.query(Publication)
            .filter(
                or_(
                    Publication.title.ilike(keyword),
                    Publication.abstract.ilike(keyword),
                    Publication.journal.ilike(keyword),
                    Publication.conference.ilike(keyword),
                    Publication.doi.ilike(keyword),
                )
            )
            .all()
        )

    @staticmethod
    def filter_and_sort(
        db: Session,
        publication_year: int | None = None,
        publication_type: str | None = None,
        status: str | None = None,
        journal: str | None = None,
        conference: str | None = None,
        sort_by: str = "publication_year",
        order: str = "desc",
    ):
        query = db.query(Publication)

        if publication_year is not None:
            query = query.filter(
                Publication.publication_year == publication_year
            )

        if publication_type:
            query = query.filter(
                Publication.publication_type == publication_type
            )

        if status:
            query = query.filter(
                Publication.status == status
            )

        if journal:
            query = query.filter(
                Publication.journal.ilike(f"%{journal}%")
            )

        if conference:
            query = query.filter(
                Publication.conference.ilike(f"%{conference}%")
            )

        sort_column = getattr(
            Publication,
            sort_by,
            Publication.publication_year,
        )

        if order.lower() == "asc":
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))

        return query.all()


publication_repository = PublicationRepository()
