from uuid import UUID

from sqlalchemy.orm import Session

from app.models.citation import Citation


class CitationRepository:

    @staticmethod
    def create(
        db: Session,
        citation: Citation,
    ):
        db.add(citation)
        db.commit()
        db.refresh(citation)
        return citation

    @staticmethod
    def get_all(
        db: Session,
    ):
        return (
            db.query(Citation)
            .order_by(Citation.created_at.desc())
            .all()
        )

    @staticmethod
    def get_by_id(
        db: Session,
        citation_id: UUID,
    ):
        return (
            db.query(Citation)
            .filter(Citation.id == citation_id)
            .first()
        )

    @staticmethod
    def get_by_publication(
        db: Session,
        publication_id: UUID,
    ):
        return (
            db.query(Citation)
            .filter(
                Citation.publication_id == publication_id
            )
            .all()
        )

    @staticmethod
    def delete(
        db: Session,
        citation: Citation,
    ):
        db.delete(citation)
        db.commit()
