from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import schemas, models
from app.models import Researcher, Collaboration


router = APIRouter(
    prefix="/collaborations",
    tags=["Collaborations"]
)


# =====================================
# GET COLLABORATORS OF A RESEARCHER
# =====================================

@router.get("/{researcher_id}")
def get_collaborators(
    researcher_id: int,
    db: Session = Depends(get_db)
):

    researcher = db.query(Researcher).filter(
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

                collaborators.add(
                    (
                        author.id,
                        author.full_name
                    )
                )


    return {

        "researcher": researcher.full_name,

        "collaborators": [

            {
                "id": cid,
                "name": cname
            }

            for cid, cname in collaborators

        ]
    }



# =====================================
# GET COMPLETE COLLABORATION NETWORK
# =====================================

@router.get("/network/all")
def get_network(
    db: Session = Depends(get_db)
):

    researchers = db.query(Researcher).all()


    nodes = []

    edges = []

    seen_edges = set()



    # Create nodes

    for researcher in researchers:

        nodes.append(
            {
                "id": researcher.id,
                "label": researcher.full_name
            }
        )



    # Create unique edges

    for researcher in researchers:


        for publication in researcher.publications:


            for coauthor in publication.authors:


                if coauthor.id != researcher.id:


                    edge = tuple(
                        sorted(
                            [
                                researcher.id,
                                coauthor.id
                            ]
                        )
                    )


                    if edge not in seen_edges:


                        edges.append(
                            {
                                "source": edge[0],
                                "target": edge[1]
                            }
                        )


                        seen_edges.add(edge)



    return {

        "nodes": nodes,

        "edges": edges

    }




# =====================================
# CREATE COLLABORATION MANUALLY
# =====================================

@router.post(
    "/",
    response_model=schemas.CollaborationResponse
)
def create_collaboration(
    collaboration: schemas.CollaborationCreate,
    db: Session = Depends(get_db)
):


    # Check duplicate collaboration

    existing = db.query(Collaboration).filter(

        Collaboration.researcher1_id == collaboration.researcher1_id,

        Collaboration.researcher2_id == collaboration.researcher2_id,

        Collaboration.publication_id == collaboration.publication_id

    ).first()



    if existing:

        raise HTTPException(
            status_code=400,
            detail="Collaboration already exists"
        )



    new_collaboration = Collaboration(

        researcher1_id=collaboration.researcher1_id,

        researcher2_id=collaboration.researcher2_id,

        publication_id=collaboration.publication_id

    )


    db.add(new_collaboration)

    db.commit()

    db.refresh(new_collaboration)



    return new_collaboration