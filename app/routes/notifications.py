from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models
from app.database import get_db

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/")
def get_notifications(db: Session = Depends(get_db)):
    """A demo-ready activity feed derived from the system's latest records."""
    items = []
    for publication in db.query(models.Publication).order_by(models.Publication.id.desc()).limit(5):
        items.append({"type": "publication", "message": f"Publication added: {publication.title}", "record_id": publication.id})
    for conference in db.query(models.Conference).order_by(models.Conference.id.desc()).limit(5):
        items.append({"type": "conference", "message": f"Conference scheduled: {conference.name}", "record_id": conference.id})
    for project in db.query(models.Project).order_by(models.Project.id.desc()).limit(5):
        items.append({"type": "project", "message": f"Project created: {project.title}", "record_id": project.id})
    return {"notifications": items[:10], "count": len(items[:10])}
