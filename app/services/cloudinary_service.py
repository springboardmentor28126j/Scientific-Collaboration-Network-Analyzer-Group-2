"""Thin wrapper around Cloudinary's upload API, kept isolated so the rest
of the app never imports the `cloudinary` SDK directly."""

import cloudinary
import cloudinary.uploader
import logging
from fastapi import UploadFile

from app.core.config import settings

logger = logging.getLogger(__name__)

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
        if not all((settings.CLOUDINARY_CLOUD_NAME, settings.CLOUDINARY_API_KEY, settings.CLOUDINARY_API_SECRET)):
            logger.warning("Cloudinary is not configured; saving institution without a logo")
            return "", ""
        contents = await file.read()
        result = cloudinary.uploader.upload(
            contents,
            folder="institution_logos",
            resource_type="image",
        )
        return result["secure_url"], result["public_id"]

    @staticmethod
    async def upload_publication_file(file: UploadFile) -> tuple[str, str]:
        """Uploads a publication attachment and returns its URL and public ID."""
        if not all((settings.CLOUDINARY_CLOUD_NAME, settings.CLOUDINARY_API_KEY, settings.CLOUDINARY_API_SECRET)):
            raise RuntimeError("File uploads require Cloudinary configuration")
        contents = await file.read()
        result = cloudinary.uploader.upload(
            contents,
            folder="publication_files",
            resource_type="auto",
        )
        return result["secure_url"], result["public_id"]
