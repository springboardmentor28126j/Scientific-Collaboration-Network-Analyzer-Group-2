from sqlalchemy.orm import Session

from app.repositories.home_repository import HomeRepository


class HomeService:

    @staticmethod
    def get_home_data(db: Session):

        researchers = HomeRepository.get_trending_researchers(db)

        trending = []

        for researcher in researchers:

            department_name = "Research Department"
            institution_name = "Unknown Institution"

            if researcher.departments:
                department = researcher.departments[0]

                department_name = department.name

                if department.institution:
                    institution_name = department.institution.name

            trending.append(
                {
                    "id": str(researcher.id),
                    "name": f"{researcher.first_name} {researcher.last_name}",
                    "department": department_name,
                    "institution_name": institution_name,
                    "publication_count": len(researcher.publications),
                    "experience": researcher.experience,
                    "avatar": None,
                }
            )

        return {
            "statistics": HomeRepository.get_statistics(db),
            "latest_publications": HomeRepository.get_latest_publications(db),
            "trending_researchers": trending,
            "top_institutions": HomeRepository.get_top_institutions(db),
            "upcoming_conferences": HomeRepository.get_upcoming_conferences(db),
        }
