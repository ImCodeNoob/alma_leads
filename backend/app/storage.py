import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}


def save_resume(file: UploadFile) -> tuple[str, str]:
    """Validate and persist an uploaded resume. Returns (original_filename, stored_path)."""
    filename = file.filename or "resume"
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Resume must be one of {sorted(ALLOWED_EXTENSIONS)}",
        )

    contents = file.file.read()
    if len(contents) > settings.max_resume_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Resume must be smaller than {settings.max_resume_size_bytes // (1024 * 1024)}MB",
        )
    if len(contents) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Resume file is empty")

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    stored_name = f"{uuid.uuid4()}{extension}"
    stored_path = upload_dir / stored_name
    stored_path.write_bytes(contents)

    return filename, str(stored_path)
