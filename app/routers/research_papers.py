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
    ResearchPaperCreate,
    ResearchPaperResponse,
    ResearchPaperUpdate
)

from app.core.auth import (
    oauth2_scheme,
    decode_access_token
)

router = APIRouter(
    prefix="/papers",
    tags=["Research Papers"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --------------------------------
# Get Logged-in User
# --------------------------------

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    payload = decode_access_token(token)

    email = payload.get("sub")

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


# --------------------------------
# Get All Papers
# --------------------------------

@router.get(
    "/",
    response_model=list[ResearchPaperResponse]
)
def get_papers(
    db: Session = Depends(get_db)
):

    return crud.get_all_papers(db)


# --------------------------------
# Search Papers
# --------------------------------

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


# --------------------------------
# Get My Papers
# --------------------------------

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


# --------------------------------
# Create Paper
# --------------------------------

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

    if pdf:

        os.makedirs("uploads", exist_ok=True)

        filename = f"{uuid.uuid4()}_{pdf.filename}"

        file_path = os.path.join("uploads", filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(pdf.file, buffer)

        paper_file = file_path

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

    return db_paper
# --------------------------------
# Delete Paper
# --------------------------------

@router.delete("/{paper_id}")
def delete_paper(
    paper_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    db_paper = crud.get_paper_by_id(
        db,
        paper_id
    )

    if not db_paper:

        raise HTTPException(
            status_code=404,
            detail="Paper not found"
        )

    if db_paper.researcher_id != current_user.id:

        raise HTTPException(
            status_code=403,
            detail="Not Authorized"
        )

    return crud.delete_paper(
        db,
        db_paper
    )