from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy import select, func, desc, asc, or_, exists
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.storage import save_upload, build_download_path
from app.db.session import get_db
from app.models.institution import Institution
from app.models.publication import Publication, PublicationAuthor
from app.models.researcher import ResearcherProfile
from app.models.user import User
from app.schemas.publication import (
    PublicationCreate, PublicationUpdate, PublicationStatusUpdate, PublicationOut, PublicationListResponse,
)
from app.models.user import User, UserRole
from app.repositories import user_repository
from app.repositories import collaboration_repository
from app.utils.audit import write_audit_log
from app.utils.notifications import notify
from app.utils.affiliation import require_verified_affiliation
import os


def _sync_collaborations(db: Session, publication: Publication) -> None:
    """
    Best-effort: keeps any already-established collaboration between this
    publication's authors fresh (strength/first/last dates). Deliberately
    swallows errors -- a hiccup here must never fail the publication
    create/update it's attached to, the same way notify() never does.
    """
    try:
        collaboration_repository.sync_all_pairs_for_publication(db, publication)
    except Exception:
        db.rollback()

router = APIRouter(prefix="/publications", tags=["Publications"])


ALLOWED_PAGE_SIZES = {10, 25, 50}


@router.get("", response_model=PublicationListResponse)
def list_publications(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, description="Must be 10, 25, or 50"),
    institution_id: int | None = Query(None),
    publication_type: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    author_id: int | None = Query(None, description="Filter to publications with this researcher as primary author or co-author"),
    year: int | None = Query(None, description="Filter to publications published in this year"),
    q: str | None = Query(None, description="Search across title, venue, author name, institution name, and year"),
    sort_by: str = Query("date", description="'date' or 'title'"),
    sort_dir: str = Query("desc", description="'asc' or 'desc'"),
    mine: bool = Query(False, description="Only publications where I'm the primary author"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if page_size not in ALLOWED_PAGE_SIZES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"page_size must be one of {sorted(ALLOWED_PAGE_SIZES)}",
        )
    if sort_by not in ("date", "title"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="sort_by must be 'date' or 'title'")
    if sort_dir not in ("asc", "desc"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="sort_dir must be 'asc' or 'desc'")

    stmt = select(Publication)
    if institution_id:
        stmt = stmt.where(Publication.institution_id == institution_id)
    if publication_type:
        stmt = stmt.where(Publication.publication_type == publication_type)
    if status_filter:
        stmt = stmt.where(Publication.status == status_filter)
    if author_id:
        stmt = stmt.where(
            or_(
                Publication.primary_author_id == author_id,
                exists(
                    select(1).select_from(PublicationAuthor).where(
                        PublicationAuthor.publication_id == Publication.publication_id,
                        PublicationAuthor.researcher_id == author_id,
                    )
                ),
            )
        )
    if year:
        stmt = stmt.where(Publication.publication_date >= date(year, 1, 1), Publication.publication_date < date(year + 1, 1, 1))
    if mine:
        profile = db.scalar(select(ResearcherProfile).where(ResearcherProfile.user_id == current_user.user_id))
        if profile is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You don't have a researcher profile yet")
        stmt = stmt.where(Publication.primary_author_id == profile.researcher_id)
    if q:
        term = f"%{q}%"
        name_match = or_(ResearcherProfile.first_name.ilike(term), ResearcherProfile.last_name.ilike(term))
        primary_author_match = exists(
            select(1).select_from(ResearcherProfile).where(
                ResearcherProfile.researcher_id == Publication.primary_author_id, name_match
            )
        )
        co_author_match = exists(
            select(1)
            .select_from(PublicationAuthor)
            .join(ResearcherProfile, ResearcherProfile.researcher_id == PublicationAuthor.researcher_id)
            .where(PublicationAuthor.publication_id == Publication.publication_id, name_match)
        )
        institution_match = exists(
            select(1).select_from(Institution).where(
                Institution.institution_id == Publication.institution_id, Institution.name.ilike(term)
            )
        )
        conditions = [
            Publication.title.ilike(term),
            Publication.venue_name.ilike(term),
            primary_author_match,
            co_author_match,
            institution_match,
        ]
        stripped = q.strip()
        if stripped.isdigit() and len(stripped) == 4:
            yr = int(stripped)
            conditions.append(
                (Publication.publication_date >= date(yr, 1, 1)) & (Publication.publication_date < date(yr + 1, 1, 1))
            )
        stmt = stmt.where(or_(*conditions))

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))

    # Newest-first by default: publication_date descending, with created_at
    # as a tiebreaker for publications that share a date or have no date
    # set yet. sort_by/sort_dir let the caller flip to alphabetical-by-title
    # or reverse the direction instead.
    order_column = Publication.title if sort_by == "title" else Publication.publication_date
    order_fn = asc if sort_dir == "asc" else desc
    stmt = (
        stmt.order_by(order_fn(order_column), desc(Publication.created_at))
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
    require_verified_affiliation(current_user)

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
        # Derived from the author's own account, not client-supplied --
        # otherwise anyone could falsely attribute a publication to any
        # institution, corrupting that institution's reports/moderation view.
        institution_id=current_user.institution_id,
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
    db.refresh(publication)

    write_audit_log(db, current_user.user_id, "CREATE", "publication", publication.publication_id)
    _sync_collaborations(db, publication)
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
    is_owner = profile is not None and publication.primary_author_id == profile.researcher_id
    if not is_owner and current_user.role != UserRole.SYSTEM_ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the primary author (or a system admin) can edit this publication")

    update_data = payload.model_dump(exclude_unset=True)
    co_author_ids = update_data.pop("co_author_ids", None)

    for field, value in update_data.items():
        setattr(publication, field, value)

    if co_author_ids is not None:
        db.query(PublicationAuthor).filter(PublicationAuthor.publication_id == publication_id).delete()
        for order, researcher_id in enumerate(co_author_ids, start=1):
            db.add(PublicationAuthor(publication_id=publication_id, researcher_id=researcher_id, author_order=order))

    db.commit()
    db.refresh(publication)
    write_audit_log(db, current_user.user_id, "UPDATE", "publication", publication.publication_id)
    if co_author_ids is not None:
        _sync_collaborations(db, publication)
    return publication


@router.patch("/{publication_id}/status", response_model=PublicationOut)
def update_publication_status(
    publication_id: int,
    payload: PublicationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in (UserRole.INSTITUTION_ADMIN, UserRole.SYSTEM_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only an institution admin can change a publication's review status",
        )

    publication = db.get(Publication, publication_id)
    if publication is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")

    author_profile = db.get(ResearcherProfile, publication.primary_author_id)
    author_user = user_repository.get_by_id(db, author_profile.user_id) if author_profile else None

    if current_user.role == UserRole.INSTITUTION_ADMIN:
        if author_user is None or author_user.institution_id != current_user.institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only review publications submitted by researchers in your own institution",
            )

    publication.status = payload.status
    db.commit()
    db.refresh(publication)
    write_audit_log(
        db, current_user.user_id, "UPDATE", "publication", publication.publication_id,
        details=f"Status changed to {payload.status.value}",
    )
    if author_user is not None and author_user.user_id != current_user.user_id:
        notify(
            db, author_user.user_id, "publication_status_changed", "Publication status updated",
            f"Your publication \"{publication.title}\" is now: {payload.status.value.replace('_', ' ')}.",
            link_url=f"/publications/{publication.publication_id}",
        )
    return publication


@router.delete("/{publication_id}", status_code=204)
def delete_publication(publication_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    publication = db.get(Publication, publication_id)
    if publication is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")

    profile = db.scalar(select(ResearcherProfile).where(ResearcherProfile.user_id == current_user.user_id))
    is_owner = profile is not None and publication.primary_author_id == profile.researcher_id
    if not is_owner and current_user.role != UserRole.SYSTEM_ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the primary author (or a system admin) can delete this publication")

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
    is_owner = profile is not None and publication.primary_author_id == profile.researcher_id
    if not is_owner and current_user.role != UserRole.SYSTEM_ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the primary author (or a system admin) can upload a file for this publication")

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
