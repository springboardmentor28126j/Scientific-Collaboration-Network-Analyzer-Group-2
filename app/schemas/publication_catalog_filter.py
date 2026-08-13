from app.models.publication import PublicationType
from app.schemas.pagination import PaginationParams


class PublicationCatalogFilter(PaginationParams):
    search: str | None = None

    publication_type: PublicationType | None = None

    sort_by: str = "published_at"

    order: str = "desc"
