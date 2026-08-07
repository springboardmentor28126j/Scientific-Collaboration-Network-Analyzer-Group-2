from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ReportBase(BaseModel):
    researcher_id: int
    report_type: str  # publication, research, collaboration, institution
    title: str
    description: Optional[str] = None
    total_count: int = 0
    year_range: Optional[str] = None
    summary: Optional[str] = None

class ReportCreate(ReportBase):
    pass

class ReportUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    total_count: Optional[int] = None
    year_range: Optional[str] = None
    summary: Optional[str] = None

class Report(ReportBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True