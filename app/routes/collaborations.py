from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
from sqlalchemy.orm import Session, selectinload, joinedload
from collections import defaultdict
from itertools import combinations

from app.database import get_db
from app import crud, schemas, models, auth
from app.models import Publication, Researcher, Collaboration
from app.notification_service import notify_all_users
from app.audit import record as record_audit
from app.permissions import current_user, scoped_collaborations_query, SYSTEM_ADMIN_ROLES


router = APIRouter(
    prefix="/collaborations",
    tags=["Collaborations"],
    dependencies=[Depends(auth.require_authenticated)]
)


# =====================================
# GET COLLABORATORS OF A RESEARCHER
# =====================================

@router.get("/researcher/{researcher_id}")
def get_collaborators(
    researcher_id: int,
    db: Session = Depends(get_db)
):

    researcher = db.query(Researcher).options(
        selectinload(Researcher.publications).selectinload(Publication.authors)
    ).filter(
        Researcher.id == researcher_id
    ).first()

    if not researcher:
        raise HTTPException(
            status_code=404,
            detail="Researcher not found"
        )

    collaborators = set()

    for pub in researcher.publications:
        for author in pub.authors:
            if author.id != researcher.id:
                collaborators.add((author.id, author.full_name))

    return {
        "researcher": researcher.full_name,
        "collaborators": [
            {"id": cid, "name": cname}
            for cid, cname in collaborators
        ]
    }


# =====================================
# BASIC NETWORK (KEEPING YOUR OLD ONE)
# =====================================

@router.get("/network/all")
def get_network(db: Session = Depends(get_db)):

    researchers = db.query(Researcher).options(
        selectinload(Researcher.publications).selectinload(Publication.authors)
    ).all()

    nodes = []
    edges = []
    seen_edges = set()

    for researcher in researchers:
        nodes.append({
            "id": researcher.id,
            "label": researcher.full_name
        })

    for researcher in researchers:
        for publication in researcher.publications:
            for coauthor in publication.authors:

                if coauthor.id != researcher.id:

                    edge = tuple(sorted([researcher.id, coauthor.id]))

                    if edge not in seen_edges:
                        edges.append({
                            "source": edge[0],
                            "target": edge[1]
                        })
                        seen_edges.add(edge)

    return {
        "nodes": nodes,
        "edges": edges
    }


# =====================================
# 🔥 ADVANCED NETWORK (NEW)
# =====================================

@router.get("/network/advanced")
def get_advanced_network(db: Session = Depends(get_db)):

    researchers = db.query(Researcher).options(
        selectinload(Researcher.publications).selectinload(Publication.authors)
    ).all()

    edge_weights = defaultdict(int)
    degree_count = defaultdict(int)
    edge_activities = defaultdict(list)
    seen_activities = defaultdict(set)

    # =====================================
    # BUILD GRAPH (COLLAB COUNT)
    # =====================================
    for researcher in researchers:
        for publication in researcher.publications:

            authors = publication.authors

            for a, b in combinations(authors, 2):

                key = tuple(sorted((a.id, b.id)))

                # weight = number of shared publications
                edge_weights[key] += 1

                # degree = number of collaborations
                degree_count[a.id] += 1
                degree_count[b.id] += 1

                # Keep the actual shared work so the network detail card can
                # explain why two researchers are connected.
                activity_key = ("publication", publication.id)
                if activity_key not in seen_activities[key]:
                    edge_activities[key].append({
                        "type": "publication",
                        "project": None,
                        "title": publication.title or "Shared publication",
                        "date": publication.publication_date.isoformat() if publication.publication_date else None,
                    })
                    seen_activities[key].add(activity_key)

    # Include collaborations created directly from the Collaboration Management page.
    for collaboration in db.query(Collaboration).all():
        if collaboration.status != "accepted":
            continue
        if collaboration.researcher1_id == collaboration.researcher2_id:
            continue
        key = tuple(sorted((collaboration.researcher1_id, collaboration.researcher2_id)))
        if key not in edge_weights:
            edge_weights[key] = 0
        edge_weights[key] += 1
        degree_count[collaboration.researcher1_id] += 1
        degree_count[collaboration.researcher2_id] += 1
        activity_key = ("collaboration", collaboration.id)
        if activity_key not in seen_activities[key]:
            publication = collaboration.publication
            edge_activities[key].append({
                "type": "project" if collaboration.project else "collaboration",
                "project": collaboration.project,
                "title": publication.title if publication else None,
                "date": publication.publication_date.isoformat() if publication and publication.publication_date else None,
            })
            seen_activities[key].add(activity_key)

    # =====================================
    # BUILD NODES (RICH DATA)
    # =====================================
    nodes = []

    for r in researchers:

        publication_count = len(r.publications)
        collaborations_count = degree_count[r.id]

        # 🔥 IMPORTANCE SCORE (for frontend sizing)
        importance = publication_count * 2 + collaborations_count

        nodes.append({
            "id": r.id,
            "label": r.full_name,

            # frontend uses this
            "publications": publication_count,
            "collaborations": collaborations_count,
            "degree": collaborations_count,

            # for coloring
            "institution": (
                r.institution.name
                if hasattr(r, "institution") and r.institution
                else "Unknown"
            ),

            # 🔥 NEW: used for advanced scaling
            "importance": importance
        })

    # =====================================
    # BUILD EDGES (WITH STRONG WEIGHT)
    # =====================================
    edges = []

    for (a, b), w in edge_weights.items():

        edges.append({
            "source": a,
            "target": b,

            # frontend uses this for thickness
            "weight": w,

            # 🔥 optional stronger visual scaling
            "strength": min(w * 2, 10),
            "activities": edge_activities[(a, b)],
        })

    # =====================================
    # RETURN CLEAN STRUCTURE
    # =====================================
    return {
        "nodes": nodes,
        "edges": edges,

        # 🔥 EXTRA (for stats panel)
        "stats": {
            "total_researchers": len(nodes),
            "total_collaborations": len(edges),
            "max_collaborations": max(degree_count.values()) if degree_count else 0
        }
    }

@router.get(
    "/",
    response_model=list[schemas.CollaborationResponse]
)
def get_collaborations(
    user: models.User = Depends(current_user), db: Session = Depends(get_db)
):
    return scoped_collaborations_query(db, user).all()


@router.get("/detailed")
def get_detailed_collaborations(user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    records = scoped_collaborations_query(db, user).options(
        joinedload(Collaboration.researcher1).joinedload(Researcher.institution),
        joinedload(Collaboration.researcher2).joinedload(Researcher.institution),
        joinedload(Collaboration.publication),
    ).order_by(Collaboration.id.desc()).all()
    return [
        {
            "id": record.id,
            "researcher1_id": record.researcher1_id,
            "researcher1_name": record.researcher1.full_name,
            "researcher1_institution": record.researcher1.institution.name if record.researcher1.institution else "Unassigned",
            "researcher2_id": record.researcher2_id,
            "researcher2_name": record.researcher2.full_name,
            "researcher2_institution": record.researcher2.institution.name if record.researcher2.institution else "Unassigned",
            "project": record.project,
            "status": record.status,
            "requested_at": record.requested_at.isoformat() if record.requested_at else None,
            "publication_id": record.publication_id,
            "publication_title": record.publication.title if record.publication else None,
        }
        for record in records
    ]


@router.put("/{collaboration_id}", response_model=schemas.CollaborationResponse)
def update_collaboration(
    collaboration_id: int,
    collaboration: schemas.CollaborationCreate,
    db: Session = Depends(get_db)
):
    if collaboration.researcher1_id == collaboration.researcher2_id:
        raise HTTPException(status_code=400, detail="Choose two different researchers")
    record = crud.update_collaboration(db, collaboration_id, collaboration)
    if not record:
        raise HTTPException(status_code=404, detail="Collaboration not found")
    return record


@router.delete("/{collaboration_id}")
def delete_collaboration(collaboration_id: int, db: Session = Depends(get_db)):
    record = crud.delete_collaboration(db, collaboration_id)
    if not record:
        raise HTTPException(status_code=404, detail="Collaboration not found")
    return {"message": "Collaboration deleted successfully", "collaboration_id": collaboration_id}


# =====================================
# CREATE COLLABORATION
# =====================================

@router.post(
    "/",
    response_model=schemas.CollaborationResponse
)
def create_collaboration(
    collaboration: schemas.CollaborationCreate,
    db: Session = Depends(get_db)
):

    researcher1_id, researcher2_id = sorted([
        collaboration.researcher1_id,
        collaboration.researcher2_id
    ])

    existing = db.query(Collaboration).filter(
        Collaboration.researcher1_id == researcher1_id,
        Collaboration.researcher2_id == researcher2_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Collaboration already exists"
        )

    collaboration.researcher1_id = researcher1_id
    collaboration.researcher2_id = researcher2_id

    created = crud.create_collaboration(db, collaboration)
    first = db.query(Researcher).filter(Researcher.id == created.researcher1_id).first()
    second = db.query(Researcher).filter(Researcher.id == created.researcher2_id).first()
    project = f" for the project '{created.project}'" if created.project else ""
    notify_all_users(db, notification_type="collaboration", title="Collaboration request created", message=f"{first.full_name if first else 'A researcher'} requested a collaboration with {second.full_name if second else 'a researcher'}{project}.", link="pages/collaborations.html")
    record_audit(db, action="created", entity_type="collaboration", entity_id=created.id, details=f"Collaboration request: {created.status}")
    return created


@router.post("/{collaboration_id}/decision")
def decide_collaboration(collaboration_id: int, decision: str, user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    record = crud.get_collaboration_by_id(db, collaboration_id)
    if not record:
        raise HTTPException(status_code=404, detail="Collaboration not found")
    if record.status != "pending":
        raise HTTPException(status_code=400, detail="This collaboration request has already been decided")
    if decision not in {"accepted", "rejected"}:
        raise HTTPException(status_code=400, detail="Decision must be accepted or rejected")
    # Only a linked participant, an institution administrator for a participant's
    # institution, or a system administrator may decide a request.
    participant_ids = {record.researcher1_id, record.researcher2_id}
    participant_institutions = {
        item.institution_id for item in db.query(Researcher).filter(Researcher.id.in_(participant_ids)).all()
    }
    allowed = user.role.lower() in SYSTEM_ADMIN_ROLES or user.researcher_id in participant_ids or (
        user.role.lower() == "institution admin" and user.institution_id in participant_institutions
    )
    if not allowed:
        raise HTTPException(status_code=403, detail="Only a collaboration participant or responsible administrator can decide this request")
    record.status = decision
    record.responded_at = datetime.now(timezone.utc)
    db.commit()
    notify_all_users(db, notification_type="collaboration", title=f"Collaboration request {decision}", message=f"A collaboration request was {decision}.", link="pages/network.html" if decision == "accepted" else "pages/collaborations.html", email=False)
    record_audit(db, action=decision, entity_type="collaboration", entity_id=record.id, user_id=user.id)
    return {"message": f"Collaboration request {decision}", "id": record.id, "status": record.status}
@router.post("/add")
def add_collaboration(
    researcher1_id: int,
    researcher2_id: int,
    db: Session = Depends(get_db)
):

    r1 = db.query(Researcher).filter(Researcher.id == researcher1_id).first()
    r2 = db.query(Researcher).filter(Researcher.id == researcher2_id).first()

    if not r1 or not r2:
        raise HTTPException(status_code=404, detail="Researcher not found")

    collab = Collaboration(
        researcher1_id=researcher1_id,
        researcher2_id=researcher2_id
    )

    db.add(collab)
    db.commit()

    return {"message": "Collaboration added successfully"}
