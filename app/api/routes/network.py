from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

# Database session dependency
from app.api.dependencies import get_db

# Models import
from app.models.researcher import Researcher
from app.models.publication import Publication

router = APIRouter(prefix="/api/v1/network", tags=["network"])

@router.get("/stats")
def get_network_stats(db: Session = Depends(get_db)):
    researchers_count = db.query(func.count(Researcher.id)).scalar() or 0
    publications_count = db.query(func.count(Publication.id)).scalar() or 0

    return {
        "researchers_count": researchers_count,
        "publications_count": publications_count,
        "collaboration_density": 0.74,
    }

@router.get("/graph")
def get_graph_data(query: str = "", db: Session = Depends(get_db)):
    # Graph data logic here
    nodes = [
        {"id": "1", "label": "Dr. Alice Smith", "role": "Principal Investigator"},
        {"id": "2", "label": "Dr. Bob Jones", "role": "Co-Author"},
    ]
    edges = [
        {"source": "1", "target": "2", "weight": 5}
    ]
    return {"nodes": nodes, "edges": edges}