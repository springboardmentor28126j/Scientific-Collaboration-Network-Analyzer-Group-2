from sqlalchemy.orm import Session

from app.repositories.search_repository import SearchRepository


class SearchService:

    @staticmethod
    def search(
        db: Session,
        query: str,
        entity_type: str = "all",
        page: int = 1,
        page_size: int = 10,
        year: int | None = None,
        publication_type: str | None = None,
        status: str | None = None,
        institution: str | None = None,
        sort: str = "relevance",
    ):

        response = {
            "query": query,
            "page": page,
            "page_size": page_size,
            "researchers": [],
            "publications": [],
            "institutions": [],
            "total": 0,
        }

        # ======================================================
        # Researchers
        # ======================================================

        if entity_type in ("all", "researchers"):

            total, researchers = SearchRepository.search_researchers(
                db=db,
                query=query,
                page=page,
                page_size=page_size,
                institution=institution,
                sort=sort,
            )

            response["researchers"] = [
                {
                    "id": str(r.id),
                    "name": f"{r.first_name} {r.last_name}",
                    "bio": r.bio,
                    "experience": r.experience,
                    "publication_count": len(r.publications),
                    "department": (
                        r.departments[0].name
                        if r.departments
                        else None
                    ),
                    "institution": (
                        r.departments[0].institution.name
                        if (
                            r.departments
                            and r.departments[0].institution
                        )
                        else None
                    ),
                }
                for r in researchers
            ]

            response["total"] += total

        # ======================================================
        # Publications
        # ======================================================

        if entity_type in ("all", "publications"):

            total, publications = SearchRepository.search_publications(
                db=db,
                query=query,
                page=page,
                page_size=page_size,
                year=year,
                publication_type=publication_type,
                status=status,
                sort=sort,
            )

            response["publications"] = [
                {
                    "id": str(p.id),
                    "title": p.title,
                    "abstract": p.abstract,
                    "journal": p.journal,
                    "conference": p.conference,
                    "publication_year": p.publication_year,
                    "publication_type": p.publication_type.value,
                    "status": p.status.value,
                    "citation_count": p.citation_count,
                    "doi": p.doi,
                    "url": p.url,
                    "authors": [
                        {"name": f"{researcher.first_name} {researcher.last_name}"}
                        for researcher in p.researchers
                    ],
                }
                for p in publications
            ]

            response["total"] += total

        # ======================================================
        # Institutions
        # ======================================================

        if entity_type in ("all", "institutions"):

            total, institutions = SearchRepository.search_institutions(
                db=db,
                query=query,
                page=page,
                page_size=page_size,
                sort=sort,
            )

            response["institutions"] = [
                {
                    "id": str(i.id),
                    "name": i.name,
                    "abbreviation": i.abbreviation,
                    "website": i.website,
                    "email": i.email,
                    "phone": i.phone,
                    "address": i.address,
                    "city": i.city,
                    "state": i.state,
                    "country": i.country,
                    "department_count": len(i.departments),
                }
                for i in institutions
            ]

            response["total"] += total

        return response
