import uuid

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class PublicationAuthorCreate(BaseModel):
    researcher_id: uuid.UUID
    author_order: int = Field(gt=0)
    is_corresponding_author: bool = False


class PublicationAuthorRead(ORMBase):
    researcher_id: uuid.UUID
    full_name: str
    institution: str | None
    author_order: int
    is_corresponding_author: bool
