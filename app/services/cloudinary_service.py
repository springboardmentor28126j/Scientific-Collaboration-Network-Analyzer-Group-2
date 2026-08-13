"""Thin wrapper around Cloudinary's upload API, kept isolated so the rest
of the app never imports the `cloudinary` SDK directly."""

import os
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile

from app.core.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)


class CloudinaryService:
    @staticmethod
    async def upload_institution_logo(file: UploadFile) -> tuple[str, str]:
        """Returns (secure_url, public_id)."""
        contents = await file.read()
        result = cloudinary.uploader.upload(
            contents,
            folder="institution_logos",
            resource_type="image",
        )
        return result["secure_url"], result["public_id"]

    @staticmethod
    async def upload_publication_pdf(file: UploadFile) -> tuple[str, str]:
        contents = await file.read()

        filename, extension = os.path.splitext(file.filename)

        extension = extension.lstrip(".").lower()

        result = cloudinary.uploader.upload(
            contents,
            folder="publication_pdfs",
            resource_type="raw",
            public_id=filename,
            format=extension,
            use_filename=True,
            unique_filename=True,
            overwrite=False,
        )

        return result["secure_url"], result["public_id"]
