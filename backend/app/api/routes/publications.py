from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.core.audit import log_audit
from app.core.email import send_email
from app.core.notifications import create_notification
from app.db.base_class import utcnow
from app.db.session import get_db
from app.models.institution import Institution
from app.models.publication import Publication, PublicationAuthor, PublicationStatus
from app.models.researcher import Researcher
from app.models.reviewer_assignment import ReviewerAssignment
from app.models.user import User, UserRole
from app.schemas.publication import (
    PublicationCreate,
    PublicationOut,
    PublicationReviewDecision,
    PublicationUpdate,
)

router = APIRouter()

UPLOAD_DIR = Path("uploads/publication_files")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _institution_id_for_admin(db: Session, current_user: User) -> int | None:
    """The single institution an Institution Admin manages, or None if
    they don't manage one yet. Same lookup as reports.py's helper of the
    same purpose -- duplicated locally per this codebase's existing
    convention rather than cross-importing between route modules."""
    institution = (
        db.query(Institution).filter(Institution.admin_user_id == current_user.id).first()
    )
    return institution.id if institution else None


def _get_current_researcher(db: Session, current_user: User) -> Researcher:
    researcher = db.query(Researcher).filter(Researcher.user_id == current_user.id).first()
    if researcher is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Create a researcher profile before adding publications",
        )
    return researcher


def _get_publication_or_404(db: Session, publication_id: int) -> Publication:
    publication = (
        db.query(Publication)
        .options(selectinload(Publication.authors))
        .filter(Publication.id == publication_id)
        .first()
    )
    if publication is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found"
        )
    return publication


def _validate_coauthor_ids(db: Session, coauthor_ids: list[int]) -> None:
    if not coauthor_ids:
        return
    found = db.query(Researcher.id).filter(Researcher.id.in_(coauthor_ids)).all()
    found_ids = {row[0] for row in found}
    missing = set(coauthor_ids) - found_ids
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Researcher id(s) not found: {sorted(missing)}",
        )


def _require_author(publication: Publication, researcher: Researcher) -> None:
    author_ids = {a.researcher_id for a in publication.authors}
    if researcher.id not in author_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only an author can modify this publication",
        )

def _is_eligible_reviewer(db: Session, user: User, publication: Publication) -> bool:
    """True if `user` may approve/reject this specific publication: they
    must hold the global 'reviewer' role AND have a ReviewerAssignment that
    either names this publication directly, or names an institution that
    one of the publication's authors belongs to."""
    if user.role != UserRole.REVIEWER:
        return False

    direct = (
        db.query(ReviewerAssignment)
        .filter(
            ReviewerAssignment.reviewer_user_id == user.id,
            ReviewerAssignment.publication_id == publication.id,
        )
        .first()
    )
    if direct is not None:
        return True

    author_institution_ids = {
        researcher.institution_id
        for researcher in (
            db.query(Researcher)
            .join(PublicationAuthor, PublicationAuthor.researcher_id == Researcher.id)
            .filter(PublicationAuthor.publication_id == publication.id)
            .all()
        )
        if researcher.institution_id is not None
    }
    if not author_institution_ids:
        return False

    institution_match = (
        db.query(ReviewerAssignment)
        .filter(
            ReviewerAssignment.reviewer_user_id == user.id,
            ReviewerAssignment.institution_id.in_(author_institution_ids),
        )
        .first()
    )
    return institution_match is not None

@router.post("", response_model=PublicationOut, status_code=status.HTTP_201_CREATED)
def create_publication(
    payload: PublicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Publication:
    if current_user.role == UserRole.INSTITUTION_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Institution Admins cannot publish their own publications",
        )
    researcher = _get_current_researcher(db, current_user)
    _validate_coauthor_ids(db, payload.coauthor_ids)

    data = payload.model_dump(exclude={"coauthor_ids"})
    publication = Publication(**data)
    db.add(publication)
    db.flush()

    author_ids = {researcher.id, *payload.coauthor_ids}
    for author_id in author_ids:
        db.add(PublicationAuthor(publication_id=publication.id, researcher_id=author_id))

    db.commit()
    db.refresh(publication)

    log_audit(
        db,
        user_id=current_user.id,
        action="publication_created",
        entity_type="publication",
        entity_id=publication.id,
        details=f"title={publication.title!r}",
    )
    return _get_publication_or_404(db, publication.id)


@router.get("", response_model=list[PublicationOut])
def list_publications(
    q: str | None = None,
    year: int | None = None,
    author_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Publication]:
    query = db.query(Publication).options(selectinload(Publication.authors))

    if current_user.role == UserRole.INSTITUTION_ADMIN:
        # Institution Admin only ever sees their own institution's
        # publications -- any author_id they pass is ignored so they
        # can't browse other institutions' authors' work by id.
        institution_id = _institution_id_for_admin(db, current_user)
        if institution_id is None:
            return []
        query = query.join(PublicationAuthor).join(
            Researcher, Researcher.id == PublicationAuthor.researcher_id
        ).filter(Researcher.institution_id == institution_id)
    elif author_id is not None:
        query = query.join(PublicationAuthor).filter(
            PublicationAuthor.researcher_id == author_id
        )

    if q:
        like = f"%{q}%"
        query = query.filter(or_(Publication.title.ilike(like), Publication.venue.ilike(like)))
    if year is not None:
        query = query.filter(Publication.year == year)
    return query.order_by(Publication.year.desc().nullslast(), Publication.id.desc()).all()

@router.get("/pending-review", response_model=list[PublicationOut])
def list_pending_review(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Publication]:
    """Submitted publications the current user is allowed to review. Must
    come before GET /{publication_id} in this file so 'pending-review'
    isn't swallowed as a publication_id. Reviewer-only: a Reviewer sees
    only what an institution- or publication-level ReviewerAssignment
    makes them eligible for -- e.g. a publication whose authors belong to
    an institution this reviewer is assigned to. System Admin is
    deliberately excluded from this queue; reviewing is a role-specific
    responsibility, not a blanket admin override (admins can still see
    everything via GET /publications or the Reports module).

    Deliberately avoids calling _is_eligible_reviewer() per publication
    (an N+1 pattern -- up to 3 DB round-trips per submitted publication)
    which was timing out this endpoint against the real remote DB once
    there were enough submitted publications. Instead this batch-loads
    the reviewer's assignments and every candidate publication's authors'
    institution_ids in a small, fixed number of queries, then filters
    in-memory."""
    if current_user.role != UserRole.REVIEWER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only a Reviewer can view the review queue",
        )

    submitted = (
        db.query(Publication)
        .options(selectinload(Publication.authors))
        .filter(Publication.status == PublicationStatus.SUBMITTED)
        .order_by(Publication.id.desc())
        .all()
    )
    if not submitted:
        return []

    # This reviewer's assignments, loaded ONCE instead of per-publication.
    assignments = (
        db.query(ReviewerAssignment)
        .filter(ReviewerAssignment.reviewer_user_id == current_user.id)
        .all()
    )
    assigned_publication_ids = {
        a.publication_id for a in assignments if a.publication_id is not None
    }
    assigned_institution_ids = {
        a.institution_id for a in assignments if a.institution_id is not None
    }
    if not assigned_publication_ids and not assigned_institution_ids:
        return []

    # Every submitted publication's authors' institution_ids, batched
    # into ONE query instead of one query per publication.
    all_researcher_ids = {
        author.researcher_id for pub in submitted for author in pub.authors
    }
    researcher_institution: dict[int, int | None] = {}
    if all_researcher_ids:
        researcher_institution = dict(
            db.query(Researcher.id, Researcher.institution_id)
            .filter(Researcher.id.in_(all_researcher_ids))
            .all()
        )

    eligible = []
    for pub in submitted:
        if pub.id in assigned_publication_ids:
            eligible.append(pub)
            continue
        author_institution_ids = {
            researcher_institution.get(author.researcher_id) for author in pub.authors
        }
        author_institution_ids.discard(None)
        if author_institution_ids & assigned_institution_ids:
            eligible.append(pub)

    return eligible


@router.get("/reviewed-by-me", response_model=list[PublicationOut])
def list_reviewed_by_me(
    decision: str | None = None,  # "approved" or "rejected", or omit for both
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Publication]:
    """Publications the current user has personally reviewed (approved or
    rejected), most recent decision first. Must come before GET
    /{publication_id} for the same routing reason as /pending-review."""
    if current_user.role not in (UserRole.REVIEWER, UserRole.SYSTEM_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only a Reviewer or System Admin can view review history",
        )

    query = (
        db.query(Publication)
        .options(selectinload(Publication.authors))
        .filter(Publication.reviewed_by == current_user.id)
    )
    if decision == "approved":
        query = query.filter(Publication.status == PublicationStatus.PUBLISHED)
    elif decision == "rejected":
        query = query.filter(Publication.status == PublicationStatus.DRAFT)

    return query.order_by(Publication.reviewed_at.desc()).all()


@router.get("/{publication_id}", response_model=PublicationOut)
def get_publication(
    publication_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Publication:
    publication = _get_publication_or_404(db, publication_id)
    if current_user.role == UserRole.INSTITUTION_ADMIN:
        institution_id = _institution_id_for_admin(db, current_user)
        author_institution_ids = {
            researcher.institution_id
            for researcher in (
                db.query(Researcher)
                .join(PublicationAuthor, PublicationAuthor.researcher_id == Researcher.id)
                .filter(PublicationAuthor.publication_id == publication_id)
                .all()
            )
        }
        if institution_id is None or institution_id not in author_institution_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This publication doesn't belong to your institution",
            )
    return publication


@router.put("/{publication_id}", response_model=PublicationOut)
def update_publication(
    publication_id: int,
    payload: PublicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Publication:
    researcher = _get_current_researcher(db, current_user)
    publication = _get_publication_or_404(db, publication_id)
    _require_author(publication, researcher)
    _validate_coauthor_ids(db, payload.coauthor_ids)

    if (
        payload.status == PublicationStatus.PUBLISHED
        and publication.status != PublicationStatus.PUBLISHED
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Authors can't publish directly. Set status to 'submitted' "
                "and wait for an assigned reviewer to approve it."
            ),
        )

    for field, value in payload.model_dump(exclude={"coauthor_ids"}).items():
        setattr(publication, field, value)

    db.query(PublicationAuthor).filter(
        PublicationAuthor.publication_id == publication.id
    ).delete()
    author_ids = {researcher.id, *payload.coauthor_ids}
    for author_id in author_ids:
        db.add(PublicationAuthor(publication_id=publication.id, researcher_id=author_id))

    db.commit()

    log_audit(
        db,
        user_id=current_user.id,
        action="publication_updated",
        entity_type="publication",
        entity_id=publication.id,
        details=f"title={publication.title!r}",
    )
    return _get_publication_or_404(db, publication_id)


@router.delete("/{publication_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_publication(
    publication_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    researcher = _get_current_researcher(db, current_user)
    publication = _get_publication_or_404(db, publication_id)
    _require_author(publication, researcher)

    title = publication.title
    db.delete(publication)
    db.commit()

    log_audit(
        db,
        user_id=current_user.id,
        action="publication_deleted",
        entity_type="publication",
        entity_id=publication_id,
        details=f"title={title!r}",
    )


@router.post("/{publication_id}/upload", response_model=PublicationOut)
async def upload_publication_file(
    publication_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Publication:
    researcher = _get_current_researcher(db, current_user)
    publication = _get_publication_or_404(db, publication_id)
    _require_author(publication, researcher)

    original_name = file.filename or "upload"
    ext = Path(original_name).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 10 MB",
        )

    stored_filename = f"{publication_id}_{uuid4().hex}{ext}"
    (UPLOAD_DIR / stored_filename).write_bytes(contents)

    publication.stored_filename = stored_filename
    publication.original_filename = original_name
    db.commit()
    return _get_publication_or_404(db, publication_id)

@router.patch("/{publication_id}/review", response_model=PublicationOut)
def review_publication(
    publication_id: int,
    payload: PublicationReviewDecision,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Publication:
    publication = _get_publication_or_404(db, publication_id)

    if publication.status != PublicationStatus.SUBMITTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only a publication with status 'submitted' can be reviewed",
        )

    if not _is_eligible_reviewer(db, current_user, publication):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not an assigned reviewer for this publication",
        )

    publication.status = (
        PublicationStatus.PUBLISHED
        if payload.decision == "approve"
        else PublicationStatus.DRAFT
    )
    publication.reviewed_by = current_user.id
    publication.review_comment = payload.comment
    publication.reviewed_at = utcnow()

    db.commit()
    db.refresh(publication)

    log_audit(
        db,
        user_id=current_user.id,
        action="publication_reviewed",
        entity_type="publication",
        entity_id=publication.id,
        details=f"decision={payload.decision}",
    )

    decision_text = (
        "approved and published" if payload.decision == "approve" else "sent back to draft"
    )
    for author_link in publication.authors:
        author_researcher = (
            db.query(Researcher).filter(Researcher.id == author_link.researcher_id).first()
        )
        if author_researcher is None:
            continue
        create_notification(
            db,
            user_id=author_researcher.user_id,
            type="publication_reviewed",
            message=f"Your publication '{publication.title}' was {decision_text}",
            link_url="/publications",
        )
        if author_researcher.user:
            send_email(
                author_researcher.user.email,
                "Publication review update",
                f"Your publication '{publication.title}' was {decision_text}.",
            )

    return _get_publication_or_404(db, publication_id)
