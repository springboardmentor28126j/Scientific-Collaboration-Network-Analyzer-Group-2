import uuid

from app.models.publication import PublicationType
from app.schemas.common import ORMBase


class PublicationReferenceLookup(ORMBase):
    id: uuid.UUID
    title: str
    abstract: str
    authors: str
    institution_name: str
    publication_name: str | None
    year: int | None
    doi: str | None
    url: str | None
    publication_type: PublicationType
