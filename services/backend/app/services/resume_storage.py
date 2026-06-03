from pathlib import Path, PurePath
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

ALLOWED_RESUME_MIME_TYPES = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
}


def _safe_original_filename(filename: str | None) -> str:
    if not filename:
        return "resume"
    name = PurePath(filename).name.strip()
    return name or "resume"


async def store_resume_upload(*, user_id: str, upload: UploadFile) -> tuple[str, str, int]:
    if upload.content_type not in ALLOWED_RESUME_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Resume must be a PDF or DOCX file.",
        )

    original_filename = _safe_original_filename(upload.filename)
    expected_suffix = ALLOWED_RESUME_MIME_TYPES[upload.content_type]
    if not original_filename.lower().endswith(expected_suffix):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Resume filename must end with {expected_suffix}.",
        )

    storage_root = Path(settings.upload_storage_dir).resolve()
    user_dir = storage_root / user_id
    user_dir.mkdir(parents=True, exist_ok=True)

    stored_filename = f"{uuid4()}{expected_suffix}"
    storage_path = user_dir / stored_filename

    total_size = 0
    try:
        with storage_path.open("wb") as destination:
            while chunk := await upload.read(1024 * 1024):
                total_size += len(chunk)
                if total_size > settings.max_upload_size_bytes:
                    raise HTTPException(
                        status_code=413,
                        detail="Resume file is too large.",
                    )
                destination.write(chunk)
    except Exception:
        storage_path.unlink(missing_ok=True)
        try:
            user_dir.rmdir()
        except OSError:
            pass
        raise
    finally:
        await upload.close()

    return str(storage_path), original_filename, total_size
