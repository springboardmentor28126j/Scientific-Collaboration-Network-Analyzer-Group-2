import uuid
from datetime import datetime

from app.models.publication import PublicationType
from app.schemas.common import ORMBase


class PublicationCatalogSearchItem(ORMBase):
    id: uuid.UUID
    title: str
    doi: str | None
    publication_type: PublicationType
    published_at: datetime | None


class PublicationCatalogItem(ORMBase):
    id: uuid.UUID
    title: str
    publication_type: PublicationType
    doi: str | None
    published_at: datetime | None
