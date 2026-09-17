from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
import models
from database import get_db


router = APIRouter(
    prefix="/files",
    tags=["Files"]
)


@router.post("/upload")
def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    new_file = models.File(
        file_name=file.filename,
        file_path="uploads/" + file.filename
    )

    db.add(new_file)
    db.commit()
    db.refresh(new_file)

    return {
        "message": "File uploaded successfully",
        "filename": file.filename
    }