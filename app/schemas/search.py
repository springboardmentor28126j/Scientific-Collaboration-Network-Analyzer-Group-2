from typing import Any

from pydantic import BaseModel


class SearchResponse(BaseModel):
    page: int
    page_size: int
    total: int

    researchers: list[Any]
    publications: list[Any]
    institutions: list[Any]
