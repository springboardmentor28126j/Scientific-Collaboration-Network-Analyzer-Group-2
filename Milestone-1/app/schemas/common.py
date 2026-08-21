from pydantic import BaseModel


class Message(BaseModel):
    """Generic response envelope for endpoints that just confirm an action."""

    detail: str


class ORMBase(BaseModel):
    model_config = {"from_attributes": True}
