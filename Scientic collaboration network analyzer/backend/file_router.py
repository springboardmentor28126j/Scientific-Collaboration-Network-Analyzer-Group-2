from fastapi import APIRouter, UploadFile, File

router = APIRouter()


@router.post("/files/upload")
def upload_file(file: UploadFile = File(...)):

    return {
        "message": "File uploaded successfully",
        "filename": file.filename
    }