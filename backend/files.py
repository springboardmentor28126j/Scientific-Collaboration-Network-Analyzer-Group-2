from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from pathlib import Path
import cloudinary
import cloudinary.uploader
import os

import models
from database import get_db

load_dotenv()

# Cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

router = APIRouter(
    prefix="/files",
    tags=["Files"]
)


@router.post("/upload")
def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Only PDF files are allowed
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    try:
        # Upload PDF to Cloudinary
        result = cloudinary.uploader.upload(
            file.file,
            resource_type="raw",
            folder="scientific_collaboration/publications",
            use_filename=True,
            unique_filename=True
        )

        cloudinary_url = result.get("secure_url")

        if not cloudinary_url:
            raise HTTPException(
                status_code=500,
                detail="Cloudinary upload failed."
            )

        # Save Cloudinary URL in database
        new_file = models.File(
            file_name=file.filename,
            file_path=cloudinary_url
        )

        db.add(new_file)
        db.commit()
        db.refresh(new_file)

        return {
            "message": "File uploaded successfully to Cloudinary",
            "filename": file.filename,
            "file_path": cloudinary_url
        }

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Cloudinary upload failed: {str(e)}"
        )