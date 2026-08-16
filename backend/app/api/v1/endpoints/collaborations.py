from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.collaboration import CollaborationRequest, CollaborationRequestStatus
from app.models.researcher import ResearcherProfile
from app.models.user import User, UserRole
from app.repositories import collaboration_repository as repo
from app.schemas.collaboration import (
    ResearcherBrief,
    CollaborationRequestCreate,
    CollaborationRequestRespond,
    CollaborationRequestOut,
    CollaborationRequestListResponse,
    SharedPublicationOut,
    CollaborationOut,
    CollaborationListResponse,
    CollaborationDetailOut,
    NetworkNode,
    NetworkEdge,
    NetworkGraphOut,
    SuggestedCollaboratorOut,
)
from app.utils.audit import write_audit_log
from app.utils.notifications import notify

router = APIRouter(tags=["Collaborations"])

ALLOWED_PAGE_SIZES = {10, 25, 50}


def _require_my_profile(db: Session, current_user: User) -> ResearcherProfile:
    profile = db.scalar(select(ResearcherProfile).where(ResearcherProfile.user_id == current_user.user_id))
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You need a researcher profile before using the collaboration network",
        )
    return profile


def _brief(researcher: ResearcherProfile) -> ResearcherBrief:
    institution_name = None
    if researcher.user is not None and researcher.user.institution is not None:
        institution_name = researcher.user.institution.name
    return ResearcherBrief(
        researcher_id=researcher.researcher_id,
        first_name=researcher.first_name,
        last_name=researcher.last_name,
        academic_title=researcher.academic_title,
        institution_name=institution_name,
        department_name=researcher.department.name if researcher.department else None,
    )


def _collaboration_out(collaboration, viewer_researcher_id: int | None = None) -> CollaborationOut:
    partner = None
    if viewer_researcher_id is not None:
        other = (
            collaboration.researcher2 if collaboration.researcher1_id == viewer_researcher_id else collaboration.researcher1
        )
        partner = _brief(other)
    return CollaborationOut(
        collaboration_id=collaboration.collaboration_id,
        researcher1=_brief(collaboration.researcher1),
        researcher2=_brief(collaboration.researcher2),
        partner=partner,
        strength=collaboration.strength,
        first_collaboration=collaboration.first_collaboration,
        last_collaboration=collaboration.last_collaboration,
        created_at=collaboration.created_at,
    )


def _request_out(req) -> CollaborationRequestOut:
    return CollaborationRequestOut(
        collaboration_request_id=req.collaboration_request_id,
        requester=_brief(req.requester),
        addressee=_brief(req.addressee),
        status=req.status,
        message=req.message,
        created_at=req.created_at,
        responded_at=req.responded_at,
    )


# --- Connect / accept flow ---

@router.post("/collaboration-request", response_model=CollaborationRequestOut, status_code=status.HTTP_201_CREATED)
def send_collaboration_request(
    payload: CollaborationRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    me = _require_my_profile(db, current_user)

    if payload.addressee_researcher_id == me.researcher_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can't connect with yourself")

    addressee = db.get(ResearcherProfile, payload.addressee_researcher_id)
    if addressee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Researcher not found")

    if repo.get_collaboration_between(db, me.researcher_id, addressee.researcher_id) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You're already collaborators")

    if repo.get_pending_request_between(db, me.researcher_id, addressee.researcher_id) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There's already a pending connection request between you and this researcher",
        )

    req = CollaborationRequest(
        requester_id=me.researcher_id, addressee_id=addressee.researcher_id, message=payload.message,
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    req = repo.get_request_by_id(db, req.collaboration_request_id)

    write_audit_log(db, current_user.user_id, "CREATE", "collaboration_request", req.collaboration_request_id)
    if addressee.user_id != current_user.user_id:
        notify(
            db, addressee.user_id, "collaboration_request_received", "New collaboration request",
            f"{me.first_name} {me.last_name} wants to connect with you.",
            link_url="/collaborations/requests",
        )
    return _request_out(req)


@router.get("/collaboration-requests", response_model=CollaborationRequestListResponse)
def list_collaboration_requests(
    direction: str | None = Query(None, description="incoming, outgoing, or omit for both"),
    status_filter: CollaborationRequestStatus | None = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if direction not in (None, "incoming", "outgoing"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="direction must be 'incoming' or 'outgoing'")
    me = _require_my_profile(db, current_user)
    items = repo.list_requests(db, me.researcher_id, direction=direction, status_filter=status_filter)
    out = [_request_out(r) for r in items]
    return CollaborationRequestListResponse(items=out, total=len(out))


@router.patch("/collaboration-request/{collaboration_request_id}", response_model=CollaborationRequestOut)
def respond_to_collaboration_request(
    collaboration_request_id: int,
    payload: CollaborationRequestRespond,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        payload.validate_is_response()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    req = repo.get_request_by_id(db, collaboration_request_id)
    if req is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collaboration request not found")

    me = _require_my_profile(db, current_user)

    if payload.status in (CollaborationRequestStatus.ACCEPTED, CollaborationRequestStatus.REJECTED):
        if req.addressee_id != me.researcher_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the addressee can accept or reject this request")
    else:  # CANCELLED
        if req.requester_id != me.researcher_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the requester can cancel this request")

    if req.status != CollaborationRequestStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This request has already been responded to")

    req.status = payload.status
    req.responded_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(req)
    write_audit_log(
        db, current_user.user_id, "UPDATE", "collaboration_request", req.collaboration_request_id,
        details=f"Status changed to {payload.status.value}",
    )

    if payload.status == CollaborationRequestStatus.ACCEPTED:
        collaboration, _ = repo.get_or_create_collaboration(db, req.requester_id, req.addressee_id)
        repo.recompute_metrics(db, collaboration)
        requester_user_id = req.requester.user_id
        if requester_user_id != current_user.user_id:
            notify(
                db, requester_user_id, "collaboration_request_accepted", "Connection request accepted",
                f"{req.addressee.first_name} {req.addressee.last_name} accepted your collaboration request.",
                link_url=f"/collaborations/{collaboration.collaboration_id}",
            )
    elif payload.status == CollaborationRequestStatus.REJECTED:
        requester_user_id = req.requester.user_id
        if requester_user_id != current_user.user_id:
            notify(
                db, requester_user_id, "collaboration_request_rejected", "Connection request declined",
                f"{req.addressee.first_name} {req.addressee.last_name} declined your collaboration request.",
            )

    req = repo.get_request_by_id(db, collaboration_request_id)
    return _request_out(req)


# --- Established collaborations ---

@router.get("/collaborations/my", response_model=CollaborationListResponse)
def my_collaborations(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, description="Must be 10, 25, or 50"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if page_size not in ALLOWED_PAGE_SIZES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"page_size must be one of {sorted(ALLOWED_PAGE_SIZES)}",
        )
    me = _require_my_profile(db, current_user)
    items, total = repo.list_for_researcher(db, me.researcher_id, page=page, page_size=page_size)
    out = [_collaboration_out(c, viewer_researcher_id=me.researcher_id) for c in items]
    return CollaborationListResponse(items=out, total=total, page=page, page_size=page_size)


@router.get("/collaborations/network", response_model=NetworkGraphOut)
def collaboration_network(
    depth: int = Query(2, ge=1, le=3),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    me = _require_my_profile(db, current_user)
    researchers, edges = repo.ego_network(db, me.researcher_id, depth=depth)

    nodes = [
        NetworkNode(
            researcher_id=r.researcher_id,
            name=f"{r.first_name} {r.last_name}",
            academic_title=r.academic_title,
            institution_name=(r.user.institution.name if r.user and r.user.institution else None),
            is_center=(r.researcher_id == me.researcher_id),
        )
        for r in researchers
    ]
    graph_edges = [
        NetworkEdge(
            collaboration_id=e.collaboration_id, researcher1_id=e.researcher1_id,
            researcher2_id=e.researcher2_id, strength=e.strength,
        )
        for e in edges
    ]
    return NetworkGraphOut(nodes=nodes, edges=graph_edges)


@router.get("/collaborations/suggested", response_model=list[SuggestedCollaboratorOut])
def suggested_collaborators(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    me = _require_my_profile(db, current_user)
    ranked = repo.suggested_collaborators(db, me.researcher_id, limit=limit)
    return [
        SuggestedCollaboratorOut(
            researcher=_brief(candidate), reason=reason, mutual_collaborator_count=mutual, shared_interest_count=shared,
        )
        for candidate, reason, mutual, shared in ranked
    ]


@router.get("/collaborations/{collaboration_id}", response_model=CollaborationDetailOut)
def get_collaboration(
    collaboration_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    collaboration = repo.get_by_id(db, collaboration_id)
    if collaboration is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collaboration not found")

    me = db.scalar(select(ResearcherProfile).where(ResearcherProfile.user_id == current_user.user_id))
    is_participant = me is not None and me.researcher_id in (collaboration.researcher1_id, collaboration.researcher2_id)
    if not is_participant and current_user.role != UserRole.SYSTEM_ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only view collaborations you're part of")

    base = _collaboration_out(collaboration, viewer_researcher_id=me.researcher_id if is_participant else None)
    shared_publications = [
        SharedPublicationOut(
            publication_id=link.publication.publication_id,
            title=link.publication.title,
            publication_date=link.publication.publication_date,
        )
        for link in collaboration.shared_publications
    ]
    return CollaborationDetailOut(**base.model_dump(), shared_publications=shared_publications)
