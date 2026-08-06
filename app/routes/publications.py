from pathlib import Path
import shutil
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app import crud, models, schemas, auth
from app.database import get_db
from app.notification_service import notify_all_users

router = APIRouter(prefix="/publications", tags=["Publications"], dependencies=[Depends(auth.require_authenticated)])
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


def _get_publication_or_404(db: Session, publication_id: int):
    publication = crud.get_publication_by_id(db, publication_id)
    if not publication:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")
    return publication


def _publication_detail(publication: models.Publication) -> dict:
    return {
        "id": publication.id,
        "title": publication.title,
        "abstract": publication.abstract,
        "publication_type": publication.publication_type,
        "status": publication.status,
        "doi": publication.doi,
        "publication_date": publication.publication_date,
        "journal_or_venue": publication.journal_or_venue,
        "institution_id": publication.institution_id,
        "file_path": publication.file_path,
        "created_at": publication.created_at,
        "authors": [{"id": author.id, "full_name": author.full_name} for author in publication.authors],
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_publication(publication: schemas.PublicationCreate, db: Session = Depends(get_db)):
    if publication.doi and db.query(models.Publication).filter(models.Publication.doi == publication.doi).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A publication with this DOI already exists")
    requested_ids = set(publication.researcher_ids)
    if requested_ids:
        found_ids = {row.id for row in db.query(models.Researcher).filter(models.Researcher.id.in_(requested_ids)).all()}
        if found_ids != requested_ids:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or more author researcher IDs do not exist")
    created = crud.create_publication(db, publication)
    notify_all_users(db, notification_type="publication", title="New publication added", message=f"{created.title} was added to the research network.", link="pages/publications.html")
    return created


@router.get("/")
def get_publications(db: Session = Depends(get_db)):
    return crud.get_publications(db)


@router.get("/status/{publication_status}", response_model=list[schemas.PublicationResponse])
def get_publications_by_status(publication_status: str, db: Session = Depends(get_db)):
    return crud.get_publications_by_status(db, publication_status)


@router.get("/institution/{institution_id}", response_model=list[schemas.PublicationResponse])
def get_publications_by_institution(institution_id: int, db: Session = Depends(get_db)):
    return crud.get_publications_by_institution(db, institution_id)


@router.post("/assign-authors")
def assign_authors(data: schemas.PublicationAuthorAssign, db: Session = Depends(get_db)):
    publication = _get_publication_or_404(db, data.publication_id)
    authors = db.query(models.Researcher).filter(models.Researcher.id.in_(set(data.researcher_ids))).all()
    if len(authors) != len(set(data.researcher_ids)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or more researchers were not found")
    existing_ids = {author.id for author in publication.authors}
    publication.authors.extend(author for author in authors if author.id not in existing_ids)
    db.commit()
    db.refresh(publication)
    return _publication_detail(publication)


@router.delete("/remove-authors")
def remove_authors(data: schemas.PublicationAuthorAssign, db: Session = Depends(get_db)):
    publication = _get_publication_or_404(db, data.publication_id)
    requested_ids = set(data.researcher_ids)
    removed_ids = [author.id for author in publication.authors if author.id in requested_ids]
    publication.authors[:] = [author for author in publication.authors if author.id not in requested_ids]
    db.commit()
    return {"message": "Authors removed successfully", "removed_author_ids": removed_ids}


@router.post("/upload/")
def upload_pdf(publication_id: int = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    publication = _get_publication_or_404(db, publication_id)
    if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are allowed")
    filename = f"{uuid.uuid4()}.pdf"
    destination = UPLOAD_DIR / filename
    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    publication.file_path = f"uploads/{filename}"
    db.commit()
    return {"message": "PDF uploaded successfully", "file_url": f"/files/{filename}"}


@router.get("/{publication_id}")
def get_publication(publication_id: int, db: Session = Depends(get_db)):
    return _publication_detail(_get_publication_or_404(db, publication_id))


@router.put("/{publication_id}")
def update_publication(publication_id: int, updated_publication: schemas.PublicationCreate, db: Session = Depends(get_db)):
    publication = _get_publication_or_404(db, publication_id)
    if updated_publication.doi:
        duplicate = db.query(models.Publication).filter(models.Publication.doi == updated_publication.doi, models.Publication.id != publication_id).first()
        if duplicate:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A publication with this DOI already exists")
    return _publication_detail(crud.update_publication(db, publication_id, updated_publication))


@router.delete("/{publication_id}")
def delete_publication(publication_id: int, db: Session = Depends(get_db)):
    publication = _get_publication_or_404(db, publication_id)
    db.query(models.Collaboration).filter(models.Collaboration.publication_id == publication_id).delete()
    db.delete(publication)
    db.commit()
    return {"message": "Publication deleted successfully", "publication_id": publication_id}
