from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.api.routes.notifications import create_notification
from app.api.deps import get_current_user
from app.core.config import settings
from app.core.email import render_email, send_email
from app.db.session import get_db
from app.models.collaboration import (
    Collaboration,
    CollaborationPublication,
    CollaborationRequest,
    CollaborationRequestStatus,
)
from app.models.publication import Publication, PublicationAuthor
from app.models.researcher import Researcher
from app.models.user import User, UserRole
from app.schemas.collaboration import (
    CollaborationDetailOut,
    CollaborationListResponse,
    CollaborationOut,
    CollaborationRequestCreate,
    CollaborationRequestListResponse,
    CollaborationRequestOut,
    CollaborationRequestRespond,
    NetworkEdge,
    NetworkGraphOut,
    NetworkNode,
    ResearcherBrief,
    SharedPublicationOut,
    SuggestedCollaboratorOut,
)

router = APIRouter()

ALLOWED_PAGE_SIZES = {10, 25, 50}


def _get_current_researcher(db: Session, current_user: User) -> Researcher:
    researcher = db.query(Researcher).filter(Researcher.user_id == current_user.id).first()
    if researcher is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Create a researcher profile before using the collaboration network",
        )
    return researcher


def _get_researcher_or_404(db: Session, researcher_id: int) -> Researcher:
    researcher = (
        db.query(Researcher)
        .options(selectinload(Researcher.user))
        .filter(Researcher.id == researcher_id)
        .first()
    )
    if researcher is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Researcher not found")
    return researcher


def _brief(researcher: Researcher) -> ResearcherBrief:
    return ResearcherBrief(
        researcher_id=researcher.id,
        email=researcher.user.email if researcher.user else "",
        department=researcher.department,
        institution_id=researcher.institution_id,
    )


def _ordered_pair(researcher_a_id: int, researcher_b_id: int) -> tuple[int, int]:
    return (
        (researcher_a_id, researcher_b_id)
        if researcher_a_id < researcher_b_id
        else (researcher_b_id, researcher_a_id)
    )


def _get_collaboration_between(db: Session, a_id: int, b_id: int) -> Collaboration | None:
    lo, hi = _ordered_pair(a_id, b_id)
    return (
        db.query(Collaboration)
        .filter(Collaboration.researcher1_id == lo, Collaboration.researcher2_id == hi)
        .first()
    )


def _get_pending_request_between(db: Session, a_id: int, b_id: int) -> CollaborationRequest | None:
    return (
        db.query(CollaborationRequest)
        .filter(
            CollaborationRequest.status == CollaborationRequestStatus.PENDING,
            or_(
                (CollaborationRequest.requester_id == a_id) & (CollaborationRequest.addressee_id == b_id),
                (CollaborationRequest.requester_id == b_id) & (CollaborationRequest.addressee_id == a_id),
            ),
        )
        .first()
    )


def _get_or_create_collaboration(db: Session, a_id: int, b_id: int) -> Collaboration:
    existing = _get_collaboration_between(db, a_id, b_id)
    if existing is not None:
        return existing
    lo, hi = _ordered_pair(a_id, b_id)
    collaboration = Collaboration(researcher1_id=lo, researcher2_id=hi)
    db.add(collaboration)
    db.commit()
    db.refresh(collaboration)
    return collaboration


def _recompute_collaboration_metrics(db: Session, collaboration: Collaboration) -> Collaboration:
    r1, r2 = collaboration.researcher1_id, collaboration.researcher2_id

    def authored_publication_ids(researcher_id: int) -> set[int]:
        rows = (
            db.query(PublicationAuthor.publication_id)
            .filter(PublicationAuthor.researcher_id == researcher_id)
            .all()
        )
        return {row[0] for row in rows}

    shared_ids = authored_publication_ids(r1) & authored_publication_ids(r2)
    existing_links = {link.publication_id: link for link in collaboration.shared_publications}

    for pub_id in shared_ids - existing_links.keys():
        db.add(CollaborationPublication(collaboration_id=collaboration.id, publication_id=pub_id))
    for pub_id, link in existing_links.items():
        if pub_id not in shared_ids:
            db.delete(link)
    db.flush()

    if shared_ids:
        years = [
            row[0]
            for row in db.query(Publication.year).filter(Publication.id.in_(shared_ids)).all()
            if row[0] is not None
        ]
        if years:
            collaboration.first_collaboration = date(min(years), 1, 1)
            collaboration.last_collaboration = date(max(years), 1, 1)

    collaboration.strength = len(shared_ids)
    db.commit()
    db.refresh(collaboration)
    return collaboration


def _collaboration_out(collaboration: Collaboration, viewer_researcher_id: int | None = None) -> CollaborationOut:
    partner = None
    if viewer_researcher_id is not None:
        other = (
            collaboration.researcher2
            if collaboration.researcher1_id == viewer_researcher_id
            else collaboration.researcher1
        )
        partner = _brief(other)
    return CollaborationOut(
        id=collaboration.id,
        researcher1=_brief(collaboration.researcher1),
        researcher2=_brief(collaboration.researcher2),
        partner=partner,
        strength=collaboration.strength,
        first_collaboration=collaboration.first_collaboration,
        last_collaboration=collaboration.last_collaboration,
        created_at=collaboration.created_at,
    )


def _request_out(req: CollaborationRequest) -> CollaborationRequestOut:
    return CollaborationRequestOut(
        id=req.id,
        requester=_brief(req.requester),
        addressee=_brief(req.addressee),
        status=req.status,
        message=req.message,
        created_at=req.created_at,
        responded_at=req.responded_at,
    )


def _collaboration_with_context(db: Session, collaboration_id: int) -> Collaboration | None:
    return (
        db.query(Collaboration)
        .options(
            selectinload(Collaboration.researcher1).selectinload(Researcher.user),
            selectinload(Collaboration.researcher2).selectinload(Researcher.user),
            selectinload(Collaboration.shared_publications).selectinload(CollaborationPublication.publication),
        )
        .filter(Collaboration.id == collaboration_id)
        .first()
    )


def _request_with_context(db: Session, request_id: int) -> CollaborationRequest | None:
    return (
        db.query(CollaborationRequest)
        .options(
            selectinload(CollaborationRequest.requester).selectinload(Researcher.user),
            selectinload(CollaborationRequest.addressee).selectinload(Researcher.user),
        )
        .filter(CollaborationRequest.id == request_id)
        .first()
    )


@router.post("/collaboration-requests", response_model=CollaborationRequestOut, status_code=status.HTTP_201_CREATED)
def send_collaboration_request(
    payload: CollaborationRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CollaborationRequestOut:
    me = _get_current_researcher(db, current_user)

    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    recent_request_count = (
        db.query(CollaborationRequest)
        .filter(
            CollaborationRequest.requester_id == me.id,
            CollaborationRequest.created_at >= one_hour_ago,
        )
        .count()
    )
    if recent_request_count >= 10:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="You've sent too many collaboration requests recently. Please try again later.",
        )

    if payload.addressee_researcher_id == me.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can't connect with yourself")

    addressee = _get_researcher_or_404(db, payload.addressee_researcher_id)

    if _get_collaboration_between(db, me.id, addressee.id) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You're already collaborators")

    if _get_pending_request_between(db, me.id, addressee.id) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There's already a pending connection request between you and this researcher",
        )

    req = CollaborationRequest(requester_id=me.id, addressee_id=addressee.id, message=payload.message)
    db.add(req)
    db.commit()
    db.refresh(req)
    create_notification(
        db,
        recipient_user_id=addressee.user_id,
        type="collaboration_request",
        message=f"{current_user.email} wants to collaborate with you",
        link="/collaborations",
    )
    send_email(
        to_email=addressee.user.email,
        subject="New collaboration request",
        html_body=render_email(
            title="New collaboration request",
            body_html=f"<p><strong>{current_user.email}</strong> wants to collaborate with you.</p>"
            + (f"<p>\"{payload.message}\"</p>" if payload.message else ""),
            cta_text="View Request",
            cta_link=f"{settings.FRONTEND_URL}/collaborations",
        ),
    )
    return _request_out(_request_with_context(db, req.id))


@router.get("/collaboration-requests", response_model=CollaborationRequestListResponse)
def list_collaboration_requests(
    direction: str | None = Query(None, description="incoming, outgoing, or omit for both"),
    status_filter: CollaborationRequestStatus | None = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CollaborationRequestListResponse:
    if direction not in (None, "incoming", "outgoing"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="direction must be 'incoming' or 'outgoing'",
        )
    me = _get_current_researcher(db, current_user)

    query = db.query(CollaborationRequest).options(
        selectinload(CollaborationRequest.requester).selectinload(Researcher.user),
        selectinload(CollaborationRequest.addressee).selectinload(Researcher.user),
    )
    if direction == "incoming":
        query = query.filter(CollaborationRequest.addressee_id == me.id)
    elif direction == "outgoing":
        query = query.filter(CollaborationRequest.requester_id == me.id)
    else:
        query = query.filter(
            or_(CollaborationRequest.addressee_id == me.id, CollaborationRequest.requester_id == me.id)
        )
    if status_filter is not None:
        query = query.filter(CollaborationRequest.status == status_filter)

    items = query.order_by(CollaborationRequest.created_at.desc()).all()
    out = [_request_out(r) for r in items]
    return CollaborationRequestListResponse(items=out, total=len(out))


@router.patch("/collaboration-requests/{request_id}", response_model=CollaborationRequestOut)
def respond_to_collaboration_request(
    request_id: int,
    payload: CollaborationRequestRespond,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CollaborationRequestOut:
    try:
        payload.validate_is_response()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    req = _request_with_context(db, request_id)
    if req is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collaboration request not found")

    me = _get_current_researcher(db, current_user)

    if payload.status in (CollaborationRequestStatus.ACCEPTED, CollaborationRequestStatus.REJECTED):
        if req.addressee_id != me.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the addressee can accept or reject this request",
            )
    else:
        if req.requester_id != me.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the requester can cancel this request",
            )

    if req.status != CollaborationRequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This request has already been responded to",
        )

    req.status = payload.status
    req.responded_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(req)
    
    if payload.status == CollaborationRequestStatus.ACCEPTED:
        create_notification(
            db,
            recipient_user_id=req.requester.user_id,
            type="collaboration_accepted",
            message=f"{req.addressee.user.email if req.addressee.user else 'A researcher'} accepted your collaboration request",
            link="/collaborations",
        )
        if req.requester.user:
            send_email(
                to_email=req.requester.user.email,
                subject="Your collaboration request was accepted",
                html_body=render_email(
                    title="Collaboration request accepted",
                    body_html=f"<p><strong>{req.addressee.user.email if req.addressee.user else 'A researcher'}</strong> accepted your collaboration request.</p>",
                    cta_text="View Collaboration",
                    cta_link=f"{settings.FRONTEND_URL}/collaborations",
                ),
            )
    elif payload.status == CollaborationRequestStatus.REJECTED:
        create_notification(
            db,
            recipient_user_id=req.requester.user_id,
            type="collaboration_rejected",
            message="Your collaboration request was declined",
            link="/collaborations",
        )
        if req.requester.user:
            send_email(
                to_email=req.requester.user.email,
                subject="Your collaboration request was declined",
                html_body=render_email(
                    title="Collaboration request declined",
                    body_html="<p>Your collaboration request was declined.</p>",
                    cta_text="View Collaborations",
                    cta_link=f"{settings.FRONTEND_URL}/collaborations",
                ),
            )

    if payload.status == CollaborationRequestStatus.ACCEPTED:
        collaboration = _get_or_create_collaboration(db, req.requester_id, req.addressee_id)
        _recompute_collaboration_metrics(db, collaboration)

    return _request_out(_request_with_context(db, request_id))


@router.get("/my", response_model=CollaborationListResponse)
def my_collaborations(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, description="Must be 10, 25, or 50"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CollaborationListResponse:
    if page_size not in ALLOWED_PAGE_SIZES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"page_size must be one of {sorted(ALLOWED_PAGE_SIZES)}",
        )
    me = _get_current_researcher(db, current_user)

    query = db.query(Collaboration).filter(
        or_(Collaboration.researcher1_id == me.id, Collaboration.researcher2_id == me.id)
    )
    total = query.count()

    items = (
        query.options(
            selectinload(Collaboration.researcher1).selectinload(Researcher.user),
            selectinload(Collaboration.researcher2).selectinload(Researcher.user),
        )
        .order_by(Collaboration.last_collaboration.desc(), Collaboration.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    out = [_collaboration_out(c, viewer_researcher_id=me.id) for c in items]
    return CollaborationListResponse(items=out, total=total, page=page, page_size=page_size)


@router.get("/network", response_model=NetworkGraphOut)
def collaboration_network(
    depth: int = Query(2, ge=1, le=3),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NetworkGraphOut:
    me = _get_current_researcher(db, current_user)
    max_nodes = 60

    visited = {me.id}
    frontier = {me.id}
    edges: dict[int, Collaboration] = {}

    for _ in range(max(1, depth)):
        if not frontier or len(visited) >= max_nodes:
            break
        rows = (
            db.query(Collaboration)
            .filter(or_(Collaboration.researcher1_id.in_(frontier), Collaboration.researcher2_id.in_(frontier)))
            .all()
        )
        next_frontier: set[int] = set()
        for collaboration in rows:
            edges[collaboration.id] = collaboration
            for rid in (collaboration.researcher1_id, collaboration.researcher2_id):
                if rid not in visited:
                    next_frontier.add(rid)
        visited |= next_frontier
        frontier = next_frontier

    node_ids = list(visited)[:max_nodes]
    researchers = (
        db.query(Researcher).options(selectinload(Researcher.user)).filter(Researcher.id.in_(node_ids)).all()
    )

    nodes = [
        NetworkNode(
            researcher_id=r.id,
            label=r.user.email if r.user else f"Researcher {r.id}",
            department=r.department,
            institution_id=r.institution_id,
            is_center=(r.id == me.id),
        )
        for r in researchers
    ]
    graph_edges = [
        NetworkEdge(
            collaboration_id=e.id,
            researcher1_id=e.researcher1_id,
            researcher2_id=e.researcher2_id,
            strength=e.strength,
        )
        for e in edges.values()
    ]
    return NetworkGraphOut(nodes=nodes, edges=graph_edges)


@router.get("/suggested", response_model=list[SuggestedCollaboratorOut])
def suggested_collaborators(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SuggestedCollaboratorOut]:
    me = _get_current_researcher(db, current_user)

    existing_collab_ids = {
        row[0] for row in db.query(Collaboration.researcher1_id).filter(Collaboration.researcher2_id == me.id).all()
    } | {
        row[0] for row in db.query(Collaboration.researcher2_id).filter(Collaboration.researcher1_id == me.id).all()
    }
    pending_ids = {
        row[0]
        for row in db.query(CollaborationRequest.addressee_id)
        .filter(CollaborationRequest.requester_id == me.id, CollaborationRequest.status == CollaborationRequestStatus.PENDING)
        .all()
    } | {
        row[0]
        for row in db.query(CollaborationRequest.requester_id)
        .filter(CollaborationRequest.addressee_id == me.id, CollaborationRequest.status == CollaborationRequestStatus.PENDING)
        .all()
    }
    excluded = existing_collab_ids | pending_ids | {me.id}

    mutual_counts: dict[int, int] = {}
    for collaborator_id in existing_collab_ids:
        their_partners = {
            row[0] for row in db.query(Collaboration.researcher1_id).filter(Collaboration.researcher2_id == collaborator_id).all()
        } | {
            row[0] for row in db.query(Collaboration.researcher2_id).filter(Collaboration.researcher1_id == collaborator_id).all()
        }
        for partner_id in their_partners - excluded:
            mutual_counts[partner_id] = mutual_counts.get(partner_id, 0) + 1

    candidate_ids = set(mutual_counts.keys())
    if me.department:
        candidate_ids |= {
            row[0]
            for row in db.query(Researcher.id)
            .filter(Researcher.department == me.department, Researcher.id.notin_(excluded))
            .all()
        }
    if me.institution_id is not None:
        candidate_ids |= {
            row[0]
            for row in db.query(Researcher.id)
            .filter(Researcher.institution_id == me.institution_id, Researcher.id.notin_(excluded))
            .all()
        }
    candidate_ids -= excluded
    if not candidate_ids:
        return []

    candidates = db.query(Researcher).options(selectinload(Researcher.user)).filter(Researcher.id.in_(candidate_ids)).all()

    results = []
    for candidate in candidates:
        mutual = mutual_counts.get(candidate.id, 0)

        if mutual > 0:
            reason = f"{mutual} mutual collaborator{'s' if mutual != 1 else ''}"
        elif me.institution_id is not None and candidate.institution_id == me.institution_id:
            reason = "Same institution as you"
        elif me.department and candidate.department == me.department:
            reason = "Same department as you"
        else:
            reason = "You might know them"

        results.append(
            SuggestedCollaboratorOut(
                researcher=_brief(candidate),
                reason=reason,
                mutual_collaborator_count=mutual,
            )
        )

    # Rank by mutual-collaborator count (rule-based, no ML/AI involved)
    results.sort(key=lambda s: s.mutual_collaborator_count, reverse=True)
    return results[:limit]


@router.get("/{collaboration_id}", response_model=CollaborationDetailOut)
def get_collaboration(
    collaboration_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CollaborationDetailOut:
    collaboration = _collaboration_with_context(db, collaboration_id)
    if collaboration is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collaboration not found")

    me = _get_current_researcher(db, current_user)
    is_participant = me.id in (collaboration.researcher1_id, collaboration.researcher2_id)
    if not is_participant and current_user.role != UserRole.SYSTEM_ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only view collaborations you're part of")

    base = _collaboration_out(collaboration, viewer_researcher_id=me.id if is_participant else None)
    shared_publications = [
        SharedPublicationOut(publication_id=link.publication.id, title=link.publication.title, year=link.publication.year)
        for link in collaboration.shared_publications
    ]
    return CollaborationDetailOut(**base.model_dump(), shared_publications=shared_publications)