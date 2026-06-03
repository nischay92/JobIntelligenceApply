from pathlib import Path
from uuid import uuid4

import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.db.models import Resume


async def parse_resume_with_ai_service(resume: Resume) -> dict:
    storage_path = Path(resume.storage_path)
    if not storage_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stored resume file was not found.",
        )

    async with httpx.AsyncClient(timeout=30) as client:
        with storage_path.open("rb") as file:
            response = await client.post(
                f"{settings.ai_service_url}/api/v1/resumes/parse",
                files={
                    "file": (
                        resume.original_filename,
                        file,
                        resume.file_mime_type,
                    )
                },
            )

    if response.status_code >= 400:
        detail = response.json().get("detail", "Resume parsing failed.")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)

    payload = response.json()
    payload["vector_id"] = f"resume-{resume.id}-{uuid4()}"
    return payload
