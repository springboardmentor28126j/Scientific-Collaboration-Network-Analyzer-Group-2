from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.routes.notifications import create_notification
from app.core.audit import log_audit
from app.core.config import settings
from app.core.email import render_email, send_email
from app.db.session import get_db
from app.models.institution import Institution
from app.models.institution_collaboration import InstitutionCollaboration, InstitutionCollaborationStatus
from app.models.user import User, UserRole
from app.schemas.institution_collaboration import (
    InstitutionCollaborationCreate,
    InstitutionCollaborationOut,
    InstitutionCollaborationStatusUpdate,
)

router = APIRouter()


def _require_own_institution_admin(db: Session, current_user: User, institution_id: int) -> Institution:
    institution = db.query(Institution).filter(Institution.id == institution_id).first()
    if institution is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found")
    if current_user.role != UserRole.SYSTEM_ADMIN and institution.admin_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only manage collaborations for an institution you administer",
        )
    return institution


@router.post("", response_model=InstitutionCollaborationOut, status_code=status.HTTP_201_CREATED)
def propose_institution_collaboration(
    my_institution_id: int,
    payload: InstitutionCollaborationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InstitutionCollaboration:
    my_institution = _require_own_institution_admin(db, current_user, my_institution_id)

    if payload.partner_institution_id == my_institution_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="An institution can't partner with itself")

    partner = db.query(Institution).filter(Institution.id == payload.partner_institution_id).first()
    if partner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partner institution not found")

    existing = db.query(InstitutionCollaboration).filter(
        or_(
            (InstitutionCollaboration.institution1_id == my_institution_id)
            & (InstitutionCollaboration.institution2_id == payload.partner_institution_id),
            (InstitutionCollaboration.institution1_id == payload.partner_institution_id)
            & (InstitutionCollaboration.institution2_id == my_institution_id),
        )
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A collaboration between these institutions already exists")

    collab = InstitutionCollaboration(
        institution1_id=my_institution_id,
        institution2_id=payload.partner_institution_id,
        title=payload.title,
        description=payload.description,
        start_date=payload.start_date,
        end_date=payload.end_date,
        created_by=current_user.id,
    )
    db.add(collab)
    db.commit()
    db.refresh(collab)

    if partner.admin_user_id:
        create_notification(
            db,
            recipient_user_id=partner.admin_user_id,
            type="institution_collaboration_proposed",
            message=f"{my_institution.name} proposed a partnership: {payload.title}",
            link="/institutions/collaborations",
        )
        partner_admin = db.query(User).filter(User.id == partner.admin_user_id).first()
        if partner_admin:
            send_email(
                to_email=partner_admin.email,
                subject=f"Partnership proposal from {my_institution.name}",
                html_body=render_email(
                    title="New Institutional Partnership Proposal",
                    body_html=f"<p><strong>{my_institution.name}</strong> proposed a partnership titled '<strong>{payload.title}</strong>'.</p><p>{payload.description or ''}</p>",
                    cta_text="Review Proposal",
                    cta_link=f"{settings.FRONTEND_URL}/institutions/collaborations",
                ),
            )

    log_audit(db, actor_user_id=current_user.id, action="institution_collaboration_proposed", entity_type="institution_collaboration", entity_id=collab.id, details=payload.title)
    return collab


@router.get("", response_model=list[InstitutionCollaborationOut])
def list_institution_collaborations(
    institution_id: int | None = None,
    db: Session = Depends(get_db),
) -> list[InstitutionCollaboration]:
    query = db.query(InstitutionCollaboration)
    if institution_id:
        query = query.filter(
            or_(
                InstitutionCollaboration.institution1_id == institution_id,
                InstitutionCollaboration.institution2_id == institution_id,
            )
        )
    return query.order_by(InstitutionCollaboration.created_at.desc()).all()


@router.patch("/{collaboration_id}/status", response_model=InstitutionCollaborationOut)
def update_institution_collaboration_status(
    collaboration_id: int,
    payload: InstitutionCollaborationStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InstitutionCollaboration:
    collab = db.query(InstitutionCollaboration).filter(InstitutionCollaboration.id == collaboration_id).first()
    if collab is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collaboration not found")

    is_admin_of_either = current_user.role == UserRole.SYSTEM_ADMIN or current_user.id in (
        collab.institution1.admin_user_id,
        collab.institution2.admin_user_id,
    )
    if not is_admin_of_either:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't administer either institution in this partnership")

    collab.status = payload.status
    db.commit()
    db.refresh(collab)
    log_audit(db, actor_user_id=current_user.id, action="institution_collaboration_status_changed", entity_type="institution_collaboration", entity_id=collab.id, details=payload.status.value)
    return collab