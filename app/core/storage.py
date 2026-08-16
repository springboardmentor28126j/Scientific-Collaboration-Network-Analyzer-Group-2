"""
File storage abstraction. Currently only "local" (disk) is implemented,
matching STORAGE_BACKEND's current default -- S3 is a placeholder for a
later milestone, same as the original architecture doc anticipated, but
isn't built yet. Callers should go through save_upload()/build_public_url()
rather than touching the filesystem directly, so swapping to S3 later only
means changing this one file.
"""
import os
import uuid
import logging

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

logger = logging.getLogger(__name__)

# Deliberately conservative -- publications realistically need PDFs, plus a
# couple of common alternates. Executables, scripts, etc. are never allowed.
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB


def _validate_upload(file: UploadFile) -> str:
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"File type '{ext}' not allowed. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )
    return ext


def save_upload(file: UploadFile, subfolder: str) -> str:
    """
    Saves an uploaded file to local disk under LOCAL_STORAGE_PATH/subfolder/,
    with a randomized filename (never trust the client-supplied filename for
    the actual storage path -- avoids path traversal and collisions).
    Returns the relative path to store in the database (e.g. in
    Publication.file_path), NOT an absolute filesystem path.
    """
    if settings.STORAGE_BACKEND != "local":
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"Storage backend '{settings.STORAGE_BACKEND}' is not implemented yet.",
        )

    ext = _validate_upload(file)

    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)
    if size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max size is {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB.",
        )

    target_dir = os.path.join(settings.LOCAL_STORAGE_PATH, subfolder)
    os.makedirs(target_dir, exist_ok=True)

    stored_filename = f"{uuid.uuid4().hex}{ext}"
    absolute_path = os.path.join(target_dir, stored_filename)

    with open(absolute_path, "wb") as out:
        out.write(file.file.read())

    relative_path = f"{subfolder}/{stored_filename}"
    logger.info("Saved upload to %s (original filename: %s)", relative_path, file.filename)
    return relative_path


def build_download_path(relative_path: str) -> str:
    """Turns a stored relative path back into an absolute filesystem path for serving."""
    return os.path.join(settings.LOCAL_STORAGE_PATH, relative_path)
