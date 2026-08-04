from uuid import UUID
from pydantic import BaseModel, ConfigDict


class DepartmentBase(BaseModel):
    institution_id: UUID
    name: str
    description: str | None = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class DepartmentResponse(DepartmentBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
