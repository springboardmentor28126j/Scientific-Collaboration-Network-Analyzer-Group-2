from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.audit import record as record_audit
from app.database import get_db
from app.permissions import current_user, is_system_admin, require_roles

router = APIRouter(prefix="/reviews", tags=["Reviews"])


def _serialize(item: models.ReviewAssignment) -> dict:
    return {
        "id": item.id,
        "publication_id": item.publication_id,
        "publication_title": item.publication.title if item.publication else "Unknown publication",
        "publication_status": item.publication.status if item.publication else None,
        "reviewer_id": item.reviewer_id,
        "reviewer_name": item.reviewer.name if item.reviewer else "Unknown reviewer",
        "assigned_by": item.assigned_by.name if item.assigned_by else "System",
        "status": item.status,
        "comments": item.comments,
        "due_date": item.due_date.isoformat() if item.due_date else None,
        "decided_at": item.decided_at.isoformat() if item.decided_at else None,
        "created_at": item.created_at.isoformat() if item.created_at else None,
    }


@router.post("/assign", status_code=status.HTTP_201_CREATED)
def assign_review(
    payload: schemas.ReviewAssignmentCreate,
    manager: models.User = Depends(require_roles("admin", "system admin", "institution admin", "publisher")),
    db: Session = Depends(get_db),
):
    publication = db.query(models.Publication).filter(models.Publication.id == payload.publication_id).first()
    reviewer = db.query(models.User).filter(models.User.id == payload.reviewer_id, models.User.account_status == "active").first()
    if not publication:
        raise HTTPException(status_code=404, detail="Publication not found")
    if not reviewer or reviewer.role.lower() != "reviewer":
        raise HTTPException(status_code=400, detail="Choose an active Reviewer account")
    if manager.role.lower() == "institution admin" and publication.institution_id != manager.institution_id:
        raise HTTPException(status_code=403, detail="You can only assign reviews for your institution's publications")
    existing = db.query(models.ReviewAssignment).filter(models.ReviewAssignment.publication_id == payload.publication_id, models.ReviewAssignment.reviewer_id == payload.reviewer_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="This reviewer is already assigned to the publication")
    item = models.ReviewAssignment(publication_id=payload.publication_id, reviewer_id=payload.reviewer_id, assigned_by_id=manager.id, due_date=payload.due_date)
    db.add(item)
    db.commit()
    db.refresh(item)
    record_audit(db, action="assigned", entity_type="review", entity_id=item.id, user_id=manager.id, details=f"{reviewer.name} assigned to {publication.title}")
    return _serialize(item)


@router.get("/eligible-reviewers")
def eligible_reviewers(_manager: models.User = Depends(require_roles("admin", "system admin", "institution admin", "publisher")), db: Session = Depends(get_db)):
    return [{"id": user.id, "name": user.name, "email": user.email} for user in db.query(models.User).filter(models.User.account_status == "active", models.User.role.ilike("reviewer")).order_by(models.User.name).all()]


@router.get("/my-queue")
def my_review_queue(user: models.User = Depends(require_roles("reviewer")), db: Session = Depends(get_db)):
    rows = db.query(models.ReviewAssignment).options(joinedload(models.ReviewAssignment.publication), joinedload(models.ReviewAssignment.reviewer), joinedload(models.ReviewAssignment.assigned_by)).filter(models.ReviewAssignment.reviewer_id == user.id).order_by(models.ReviewAssignment.due_date.asc().nullslast(), models.ReviewAssignment.id.desc()).all()
    return [_serialize(item) for item in rows]


@router.get("/")
def all_reviews(user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    query = db.query(models.ReviewAssignment).options(joinedload(models.ReviewAssignment.publication), joinedload(models.ReviewAssignment.reviewer), joinedload(models.ReviewAssignment.assigned_by))
    if user.role.lower() == "reviewer":
        query = query.filter(models.ReviewAssignment.reviewer_id == user.id)
    elif user.role.lower() == "institution admin":
        query = query.join(models.Publication).filter(models.Publication.institution_id == user.institution_id)
    elif not is_system_admin(user) and user.role.lower() != "publisher":
        query = query.filter(False)
    return [_serialize(item) for item in query.order_by(models.ReviewAssignment.id.desc()).all()]


@router.post("/{review_id}/decision")
def decide_review(
    review_id: int,
    payload: schemas.ReviewDecision,
    reviewer: models.User = Depends(require_roles("reviewer")),
    db: Session = Depends(get_db),
):
    item = db.query(models.ReviewAssignment).options(joinedload(models.ReviewAssignment.publication)).filter(models.ReviewAssignment.id == review_id, models.ReviewAssignment.reviewer_id == reviewer.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Assigned review not found")
    decision = payload.decision.strip().lower().replace(" ", "_")
    if decision not in {"approved", "changes_requested", "rejected"}:
        raise HTTPException(status_code=400, detail="Decision must be approved, changes_requested, or rejected")
    item.status, item.comments, item.decided_at = decision, payload.comments.strip(), datetime.now(timezone.utc)
    db.commit()
    record_audit(db, action=decision, entity_type="review", entity_id=item.id, user_id=reviewer.id, details=item.publication.title if item.publication else None)
    return _serialize(item)
