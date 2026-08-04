from pydantic import BaseModel


class HomeAnalyticsResponse(BaseModel):
    researchers: int
    publications: int
    institutions: int
    conferences: int
