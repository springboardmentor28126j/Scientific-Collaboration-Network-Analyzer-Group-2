from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from collections import defaultdict
from itertools import combinations

from app.database import get_db
from app import crud, schemas, models
from app.models import Publication, Researcher, Collaboration


router = APIRouter(
    prefix="/collaborations",
    tags=["Collaborations"]
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
            "strength": min(w * 2, 10)
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
    db: Session = Depends(get_db)
):
    return crud.get_collaborations(db)


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

    return crud.create_collaboration(db, collaboration)
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
