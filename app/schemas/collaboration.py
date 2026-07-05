from pydantic import BaseModel


class CollaborationBase(BaseModel):
    researcher_1_id: int
    researcher_2_id: int
    paper_id: int
    collaboration_year: int


class CollaborationCreate(CollaborationBase):
    pass


class CollaborationResponse(CollaborationBase):
    id: int

    class Config:
        from_attributes = True