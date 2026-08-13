from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.permissions import current_user, require_roles, scoped_researchers_query
from app import models, schemas, crud, auth
from app.audit import record as record_audit

router = APIRouter(
    prefix="/researchers",
    tags=["Researchers"],
    dependencies=[Depends(auth.require_authenticated)]
)

@router.post("/")
def create_researcher(
    researcher: schemas.ResearcherCreate,
    manager: models.User = Depends(require_roles("admin", "system admin", "institution admin")),
    db: Session = Depends(get_db)
):
    created = crud.create_researcher(db=db, researcher=researcher)
    record_audit(db, action="created", entity_type="researcher", entity_id=created.id, user_id=manager.id, actor_role=manager.role, details=created.full_name)
    # When an administrator creates a profile using an account email, link it
    # automatically so the researcher dashboard becomes genuinely personal.
    if created.email:
        user = db.query(models.User).filter(models.User.email == created.email).first()
        if user and not user.researcher_id:
            user.researcher_id = created.id
            db.commit()
    return created

@router.get("/")
def get_researchers(user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    return scoped_researchers_query(db, user).order_by(models.Researcher.full_name).all()

@router.get("/{id}")
def get_researcher(id: int, user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    return scoped_researchers_query(db, user).filter(models.Researcher.id == id).first()

@router.put("/{id}")
def update_researcher(
    id: int,
    updated: schemas.ResearcherCreate,
    manager: models.User = Depends(require_roles("admin", "system admin", "institution admin")),
    db: Session = Depends(get_db)
):
    researcher = crud.update_researcher(db=db, id=id, updated=updated)
    if researcher:
        record_audit(db, action="updated", entity_type="researcher", entity_id=id, user_id=manager.id, actor_role=manager.role, details=researcher.full_name)
    return researcher
