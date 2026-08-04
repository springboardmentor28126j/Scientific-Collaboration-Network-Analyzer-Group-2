from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.publication import Publication
from app.models.institution import Institution
from app.models.conference import Conference


class AnalyticsService:

    @staticmethod
    def get_home_analytics(db: Session):
        return {
            "researchers": (
                db.query(User)
                .filter(User.role == UserRole.RESEARCHER)
                .count()
            ),
            "publications": db.query(Publication).count(),
            "institutions": db.query(Institution).count(),
            "conferences": db.query(Conference).count(),
        }


analytics_service = AnalyticsService()
