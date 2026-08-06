from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import crud, models, schemas, auth
from app.database import get_db
from app.notification_service import notify_all_users

router = APIRouter(
    prefix="/citations",
    tags=["Citations"],
    dependencies=[Depends(auth.require_authenticated)]
)

@router.post("/", response_model=schemas.CitationResponse)
def create_citation(citation: schemas.CitationCreate, db: Session = Depends(get_db)):
    created = crud.create_citation(db, citation)
    publication = db.query(models.Publication).filter(models.Publication.id == citation.citing_publication_id).first()
    notify_all_users(db, notification_type="citation", title="New citation recorded", message=f"A citation was added for {publication.title if publication else 'a publication'}.", link="pages/citations.html", email=False)
    return created

@router.get("/", response_model=list[schemas.CitationResponse])
def get_citations(db: Session = Depends(get_db)):
    return crud.get_citations(db)
