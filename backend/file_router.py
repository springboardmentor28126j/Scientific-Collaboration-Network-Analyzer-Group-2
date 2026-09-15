from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import shutil

router = APIRouter()

# Folder where uploaded PDF files will be stored
UPLOAD_FOLDER = "uploads"

# Create uploads folder if it does not exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/files/upload")
def upload_file(file: UploadFile = File(...)):

    # Check that the uploaded file is a PDF
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    # Create file path
    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    # Save the uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "File uploaded successfully",
        "filename": file.filename,
        "file_path": file_path
    }