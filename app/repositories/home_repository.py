from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.researcher import Researcher
from app.models.publication import Publication
from app.models.institution import Institution
from app.models.conference import Conference


class HomeRepository:

    @staticmethod
    def get_statistics(db: Session):
        return {
            "researchers": db.query(func.count(Researcher.id)).scalar() or 0,
            "publications": db.query(func.count(Publication.id)).scalar() or 0,
            "institutions": db.query(func.count(Institution.id)).scalar() or 0,
            "conferences": db.query(func.count(Conference.id)).scalar() or 0,
        }

    @staticmethod
    def get_latest_publications(db: Session, limit: int = 5):
        return (
            db.query(Publication)
            .order_by(Publication.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_trending_researchers(db: Session, limit: int = 6):
        return (
            db.query(Researcher)
            .order_by(Researcher.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_top_institutions(db: Session, limit: int = 6):
        return (
            db.query(Institution)
            .order_by(Institution.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_upcoming_conferences(db: Session, limit: int = 5):
        return (
            db.query(Conference)
            .order_by(Conference.created_at.desc())
            .limit(limit)
            .all()
        )
