from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form
)
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app import crud

import os
import shutil
import uuid

from app.models.research_paper import ResearchPaper
from app.models.user import User

from app.schemas.research_paper import (
    ResearchPaperResponse
)

from app.core.auth import (
    oauth2_scheme,
    decode_access_token
)
from app.services.ai_recommendation import recommend_papers


router = APIRouter(
    prefix="/papers",
    tags=["Research Papers"]
)


# ==========================================
# DATABASE
# ==========================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ==========================================
# GET LOGGED-IN USER
# ==========================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    payload = decode_access_token(token)

    if not payload:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    email = payload.get("sub")

    if not email:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = crud.get_user_by_email(
        db,
        email
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


# ==========================================
# GET ALL PAPERS
# ==========================================

@router.get(
    "/",
    response_model=list[ResearchPaperResponse]
)
def get_papers(
    db: Session = Depends(get_db)
):

    return crud.get_all_papers(db)


# ==========================================
# SEARCH PAPERS
# ==========================================

@router.get(
    "/search",
    response_model=list[ResearchPaperResponse]
)
def search_papers(
    title: str,
    db: Session = Depends(get_db)
):

    return crud.search_papers_by_title(
        db,
        title
    )


# ==========================================
# GET MY PAPERS
# ==========================================

@router.get(
    "/my-papers",
    response_model=list[ResearchPaperResponse]
)
def my_papers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return crud.get_my_papers(
        db,
        current_user.id
    )


# ==========================================
# CREATE PAPER
# ==========================================

@router.post(
    "/",
    response_model=ResearchPaperResponse
)
def create_paper(

    title: str = Form(...),
    authors: str = Form(...),
    abstract: str = Form(...),
    publication_year: int = Form(...),
    source: str = Form(...),
    doi: str = Form(...),
    keywords: str = Form(None),
    status: str = Form("Draft"),

    pdf: UploadFile = File(None),

    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)

):

    paper_file = ""

    # --------------------------------------
    # Upload PDF
    # --------------------------------------

    if pdf:

        os.makedirs(
            "uploads",
            exist_ok=True
        )

        filename = (
            f"{uuid.uuid4()}_{pdf.filename}"
        )

        file_path = os.path.join(
            "uploads",
            filename
        )

        with open(
            file_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                pdf.file,
                buffer
            )

        paper_file = file_path

    # --------------------------------------
    # Create Paper
    # --------------------------------------

    db_paper = ResearchPaper(

        title=title,
        authors=authors,
        abstract=abstract,
        publication_year=publication_year,
        source=source,
        doi=doi,
        keywords=keywords,
        status=status,
        paper_file=paper_file,
        researcher_id=current_user.id

    )

    db.add(db_paper)

    db.commit()

    db.refresh(db_paper)

    # --------------------------------------
    # AUDIT LOG
    # --------------------------------------

    crud.create_audit_log(

        db=db,

        user_id=current_user.id,

        action="PAPER_CREATED",

        module="Research Papers",

        description=(
            f"User {current_user.username} "
            f"created research paper "
            f"'{title}'"
        )

    )

    return db_paper


# ==========================================
# DELETE PAPER
# ==========================================

@router.delete(
    "/{paper_id}"
)
def delete_paper(

    paper_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)

):

    # --------------------------------------
    # Find Paper
    # --------------------------------------

    db_paper = crud.get_paper_by_id(
        db,
        paper_id
    )

    if not db_paper:

        raise HTTPException(
            status_code=404,
            detail="Paper not found"
        )

    # --------------------------------------
    # Authorization
    # --------------------------------------

    if (
        db_paper.researcher_id
        != current_user.id
    ):

        # Audit unauthorized attempt

        crud.create_audit_log(

            db=db,

            user_id=current_user.id,

            action="PAPER_DELETE_UNAUTHORIZED",

            module="Research Papers",

            description=(
                f"User {current_user.username} "
                f"attempted to delete paper "
                f"'{db_paper.title}' "
                f"without authorization"
            )

        )

        raise HTTPException(
            status_code=403,
            detail="Not Authorized"
        )

    # --------------------------------------
    # Delete Paper
    # --------------------------------------

    paper_title = db_paper.title

    result = crud.delete_paper(
        db,
        db_paper
    )

    # --------------------------------------
    # Audit Successful Delete
    # --------------------------------------

    crud.create_audit_log(

        db=db,

        user_id=current_user.id,

        action="PAPER_DELETED",

        module="Research Papers",

        description=(
            f"User {current_user.username} "
            f"deleted research paper "
            f"'{paper_title}'"
        )

    )

    return result
# ==========================================
# AI PAPER RECOMMENDATIONS
# ==========================================

@router.get("/ai-recommendations")
def ai_recommendations(
    interest: str,
    top_n: int = 5,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Recommend research papers using
    semantic similarity with AI embeddings.
    """

    papers = crud.get_all_papers(db)

    recommendations = recommend_papers(
        user_interest=interest,
        papers=papers,
        top_n=top_n
    )

    return [
        {
            "id": item["paper"].id,
            "title": item["paper"].title,
            "authors": item["paper"].authors,
            "abstract": item["paper"].abstract,
            "publication_year": item["paper"].publication_year,
            "source": item["paper"].source,
            "doi": item["paper"].doi,
            "keywords": item["paper"].keywords,
            "similarity": item["similarity"]
        }
        for item in recommendations
    ]