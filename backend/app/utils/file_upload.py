import os
import shutil
from fastapi import UploadFile

UPLOAD_DIR = "uploads"

def save_upload_file(upload_file: UploadFile) -> str:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, upload_file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return file_path
