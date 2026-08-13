from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import crud, models, schemas, auth
from app.database import get_db
from app.notification_service import notify_all_users
from app.permissions import require_roles
from app.audit import record as record_audit

router = APIRouter(
    prefix="/citations",
    tags=["Citations"],
    dependencies=[Depends(auth.require_authenticated)]
)

@router.post("/", response_model=schemas.CitationResponse)
def create_citation(citation: schemas.CitationCreate, editor: models.User = Depends(require_roles("admin", "system admin", "institution admin", "publisher", "reviewer")), db: Session = Depends(get_db)):
    created = crud.create_citation(db, citation)
    record_audit(db, action="created", entity_type="citation", entity_id=created.id, user_id=editor.id, details=f"Publication {citation.citing_publication_id} cites {citation.cited_publication_id}")
    publication = db.query(models.Publication).filter(models.Publication.id == citation.citing_publication_id).first()
    notify_all_users(db, notification_type="citation", title="New citation recorded", message=f"A citation was added for {publication.title if publication else 'a publication'}.", link="pages/citations.html", email=False)
    return created

@router.get("/", response_model=list[schemas.CitationResponse])
def get_citations(db: Session = Depends(get_db)):
    return crud.get_citations(db)
