from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy import select, func, desc
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.storage import save_upload, build_download_path
from app.db.session import get_db
from app.models.publication import Publication, PublicationAuthor
from app.models.researcher import ResearcherProfile
from app.models.user import User
from app.schemas.publication import (
    PublicationCreate, PublicationUpdate, PublicationOut, PublicationListResponse,
)
from app.utils.audit import write_audit_log
import os

router = APIRouter(prefix="/publications", tags=["Publications"])


ALLOWED_PAGE_SIZES = {10, 25, 50}


@router.get("", response_model=PublicationListResponse)
def list_publications(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, description="Must be 10, 25, or 50"),
    institution_id: int | None = Query(None),
    publication_type: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if page_size not in ALLOWED_PAGE_SIZES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"page_size must be one of {sorted(ALLOWED_PAGE_SIZES)}",
        )

    stmt = select(Publication)
    if institution_id:
        stmt = stmt.where(Publication.institution_id == institution_id)
    if publication_type:
        stmt = stmt.where(Publication.publication_type == publication_type)
    if status_filter:
        stmt = stmt.where(Publication.status == status_filter)

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))

    # Newest-first: publication_date descending, with created_at as a
    # tiebreaker for publications that share a date or have no date set yet.
    stmt = (
        stmt.order_by(desc(Publication.publication_date), desc(Publication.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = list(db.scalars(stmt).all())

    return PublicationListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{publication_id}", response_model=PublicationOut)
def get_publication(publication_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    publication = db.get(Publication, publication_id)
    if publication is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")
    return publication


@router.post("", response_model=PublicationOut, status_code=status.HTTP_201_CREATED)
def create_publication(
    payload: PublicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = db.scalar(select(ResearcherProfile).where(ResearcherProfile.user_id == current_user.user_id))
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You need a researcher profile before creating a publication",
        )

    publication = Publication(
        title=payload.title,
        abstract=payload.abstract,
        publication_type=payload.publication_type,
        primary_author_id=profile.researcher_id,
        institution_id=payload.institution_id,
        venue_name=payload.venue_name,
        doi=payload.doi,
        publication_date=payload.publication_date,
        file_path=payload.file_path,
    )
    db.add(publication)
    db.commit()
    db.refresh(publication)

    for order, researcher_id in enumerate(payload.co_author_ids, start=1):
        db.add(PublicationAuthor(publication_id=publication.publication_id, researcher_id=researcher_id, author_order=order))
    db.commit()

    write_audit_log(db, current_user.user_id, "CREATE", "publication", publication.publication_id)
    return publication


@router.patch("/{publication_id}", response_model=PublicationOut)
def update_publication(
    publication_id: int,
    payload: PublicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    publication = db.get(Publication, publication_id)
    if publication is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")

    profile = db.scalar(select(ResearcherProfile).where(ResearcherProfile.user_id == current_user.user_id))
    if profile is None or publication.primary_author_id != profile.researcher_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the primary author can edit this publication")

    update_data = payload.model_dump(exclude_unset=True)
    co_author_ids = update_data.pop("co_author_ids", None)

    for field, value in update_data.items():
        setattr(publication, field, value)

    if co_author_ids is not None:
        # Replace the full co-author list rather than append -- editing
        # needs to support removing people, not just adding.
        db.query(PublicationAuthor).filter(PublicationAuthor.publication_id == publication_id).delete()
        for order, researcher_id in enumerate(co_author_ids, start=1):
            db.add(PublicationAuthor(publication_id=publication_id, researcher_id=researcher_id, author_order=order))

    db.commit()
    db.refresh(publication)
    write_audit_log(db, current_user.user_id, "UPDATE", "publication", publication.publication_id)
    return publication


@router.delete("/{publication_id}", status_code=204)
def delete_publication(publication_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    publication = db.get(Publication, publication_id)
    if publication is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")

    profile = db.scalar(select(ResearcherProfile).where(ResearcherProfile.user_id == current_user.user_id))
    if profile is None or publication.primary_author_id != profile.researcher_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the primary author can delete this publication")

    write_audit_log(db, current_user.user_id, "DELETE", "publication", publication_id)
    db.delete(publication)
    db.commit()
    return None


@router.post("/{publication_id}/upload", response_model=PublicationOut)
def upload_publication_file(
    publication_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    publication = db.get(Publication, publication_id)
    if publication is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")

    profile = db.scalar(select(ResearcherProfile).where(ResearcherProfile.user_id == current_user.user_id))
    if profile is None or publication.primary_author_id != profile.researcher_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the primary author can upload a file for this publication")

    relative_path = save_upload(file, subfolder=f"publications/{publication_id}")

    publication.file_path = relative_path
    db.commit()
    db.refresh(publication)
    write_audit_log(db, current_user.user_id, "UPDATE", "publication", publication.publication_id, details="File uploaded")
    return publication


@router.get("/{publication_id}/download")
def download_publication_file(
    publication_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    publication = db.get(Publication, publication_id)
    if publication is None or not publication.file_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No file uploaded for this publication")

    absolute_path = build_download_path(publication.file_path)
    if not os.path.exists(absolute_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File is missing from storage")

    filename = f"{publication.title[:50]}{os.path.splitext(absolute_path)[1]}"
    return FileResponse(absolute_path, filename=filename)
