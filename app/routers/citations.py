from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models
from .. import schemas, crud
from ..database import get_db
from app.models import User
from app.oauth2 import get_current_user


router = APIRouter(
    prefix="/citations",
    tags=["Citations"]
)


@router.post("/", response_model=schemas.CitationResponse)
def create_citation(
    citation: schemas.CitationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    citing_publication = db.query(models.Publication).filter(
        models.Publication.id == citation.publication_id
    ).first()


    if not citing_publication:
        raise HTTPException(
            status_code=404,
            detail="Citing publication not found"
        )


    # ================= ROLE PERMISSION =================


    if current_user.role == "researcher":


        researcher = db.query(models.Researcher).filter(
            models.Researcher.user_id == current_user.id
        ).first()


        if not researcher:
            raise HTTPException(
                status_code=404,
                detail="Researcher profile not found"
            )


        if citing_publication.researcher_id != researcher.id:

            raise HTTPException(
                status_code=403,
                detail="You can add citation only for your own publication"
            )



    elif current_user.role == "institution_admin":


        institution_admin = db.query(models.Institution).filter(
            models.Institution.user_id == current_user.id
        ).first()


        if not institution_admin:

            raise HTTPException(
                status_code=404,
                detail="Institution profile not found"
            )


        researcher = db.query(models.Researcher).filter(
            models.Researcher.id == citing_publication.researcher_id
        ).first()



        if researcher.institution != institution_admin.name:

            raise HTTPException(
                status_code=403,
                detail="You can add citation only for researchers in your institution"
            )



    elif current_user.role == "system_admin":

        pass



    else:

        raise HTTPException(
            status_code=403,
            detail="Permission denied"
        )



    # ================= VALIDATIONS =================


    if citation.publication_id == citation.cited_publication_id:

        raise HTTPException(
            status_code=400,
            detail="A publication cannot cite itself"
        )



    cited_publication = db.query(models.Publication).filter(
        models.Publication.id == citation.cited_publication_id
    ).first()



    if not cited_publication:

        raise HTTPException(
            status_code=404,
            detail="Cited publication not found"
        )



    if cited_publication.status != "Published":

        raise HTTPException(
            status_code=400,
            detail="Only published publications can be cited"
        )



    existing = db.query(models.Citation).filter(
        models.Citation.publication_id == citation.publication_id,
        models.Citation.cited_publication_id == citation.cited_publication_id
    ).first()



    if existing:

        raise HTTPException(
            status_code=400,
            detail="Citation already exists"
        )



    # ================= CREATE + NOTIFICATION =================


    return crud.create_citation(
        db,
        citation,
        current_user.id,
        current_user.role
    )
@router.get("/")
def get_all_citations(
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "date",
    order: str = "desc",
    db: Session = Depends(get_db)
):

    citations, pagination = crud.get_all_citations(
        db,
        page,
        page_size,
        sort_by,
        order
    )

    result = []

    for citation in citations:

        result.append({

            "id": citation.id,

            "publication_id": citation.publication_id,

            "cited_publication_id": citation.cited_publication_id,

            "publication_title":
                citation.publication.title
                if citation.publication
                else "Unknown",

            "cited_publication_title":
                citation.cited_publication.title
                if citation.cited_publication
                else "Unknown",

            "created_at": citation.created_at
        })

    return {
        "data": result,
        "pagination": pagination
    }

# Get citations of a publication
@router.get("/{publication_id}", response_model=list[schemas.CitationResponse])
def get_citations(
    publication_id: int,
    db: Session = Depends(get_db)
):

    return crud.get_citations_by_publication(
        db,
        publication_id
    )


# Delete Citation
@router.delete("/{citation_id}")
def delete_citation(
    citation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    citation = db.query(models.Citation).filter(
        models.Citation.id == citation_id
    ).first()


    if not citation:
        raise HTTPException(
            status_code=404,
            detail="Citation not found"
        )


    # System Admin can delete any citation
    if current_user.role == "system_admin":
        pass


    # Researcher can delete only citations of their own publication
    elif current_user.role == "researcher":

        publication = db.query(models.Publication).filter(
            models.Publication.id == citation.publication_id
        ).first()


        if not publication:
            raise HTTPException(
                status_code=404,
                detail="Publication not found"
            )


        if publication.researcher_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can delete only your own citation records"
            )


    else:
        raise HTTPException(
            status_code=403,
            detail="Permission denied"
        )


    db.delete(citation)
    db.commit()


    return {
        "message": "Citation deleted successfully"
    }