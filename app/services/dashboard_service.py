from sqlalchemy.orm import Session

from app.repositories.dashboard_repository import DashboardRepository


class DashboardService:

    @staticmethod
    def get_statistics(db: Session):
        return DashboardRepository.get_statistics(db)

    @staticmethod
    def publications_per_year(db: Session):
        return DashboardRepository.publications_per_year(db)

    @staticmethod
    def publication_types(db: Session):
        return DashboardRepository.publication_types(db)
