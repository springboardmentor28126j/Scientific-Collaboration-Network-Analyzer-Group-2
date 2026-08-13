from uuid import UUID

from pydantic import BaseModel


class DashboardFilter(BaseModel):
    institution_id: UUID | None = None
    researcher_id: UUID | None = None
    reviewer_id: UUID | None = None
