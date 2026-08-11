from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(
    prefix="/api/v1/conferences",
    tags=["Conferences"],
)

class ConferenceSchema(BaseModel):
    acronym: str
    name: str
    location: Optional[str] = "Online"
    year: Optional[int] = 2024
    impactScore: Optional[str] = "9.0/10"
    website: Optional[str] = None

conferences_db = [
    {"id": 1, "acronym": "KDD 2024", "name": "ACM SIGKDD Conference on Knowledge Discovery and Data Mining", "location": "Barcelona, Spain", "year": 2024, "impactScore": "9.8/10"},
    {"id": 2, "acronym": "NeurIPS 2024", "name": "Conference on Neural Information Processing Systems", "location": "Vancouver, Canada", "year": 2024, "impactScore": "9.9/10"},
    {"id": 3, "acronym": "ICSE 2024", "name": "International Conference on Software Engineering", "location": "Lisbon, Portugal", "year": 2024, "impactScore": "9.2/10"}
]

@router.get("/", response_model=List[dict])
def get_all_conferences():
    return conferences_db

@router.get("/{conf_id}")
def get_conference(conf_id: int):
    for c in conferences_db:
        if c["id"] == conf_id:
            return c
    raise HTTPException(status_code=404, detail="Conference not found")

@router.post("/", status_code=201)
def create_conference(conf: ConferenceSchema):
    new_id = len(conferences_db) + 1
    item = conf.dict()
    item["id"] = new_id
    conferences_db.append(item)
    return item

@router.put("/{conf_id}")
def update_conference(conf_id: int, conf: ConferenceSchema):
    for idx, c in enumerate(conferences_db):
        if c["id"] == conf_id:
            updated = conf.dict()
            updated["id"] = conf_id
            conferences_db[idx] = updated
            return updated
    raise HTTPException(status_code=404, detail="Conference not found")
