from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.researcher import Researcher
from app.models.publication import Publication
from app.models.conference import Conference
from app.models.institution import Institution


class DashboardRepository:

    @staticmethod
    def get_statistics(db: Session):
        return {
            "researchers": db.query(func.count(Researcher.id)).scalar() or 0,
            "publications": db.query(func.count(Publication.id)).scalar() or 0,
            "conferences": db.query(func.count(Conference.id)).scalar() or 0,
            "institutions": db.query(func.count(Institution.id)).scalar() or 0,
        }

    @staticmethod
    def publications_per_year(db: Session):
        rows = (
            db.query(
                Publication.publication_year.label("year"),
                func.count(Publication.id).label("count"),
            )
            .group_by(Publication.publication_year)
            .order_by(Publication.publication_year)
            .all()
        )

        return [
            {
                "year": row.year,
                "count": row.count,
            }
            for row in rows
        ]

    @staticmethod
    def publication_types(db: Session):
        rows = (
            db.query(
                Publication.publication_type.label("type"),
                func.count(Publication.id).label("count"),
            )
            .group_by(Publication.publication_type)
            .all()
        )

        return [
            {
                "type": row.type,
                "count": row.count,
            }
            for row in rows
        ]
