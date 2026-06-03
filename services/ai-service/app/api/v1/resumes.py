from typing import Annotated

from fastapi import APIRouter, File, UploadFile

from app.parsers.resumes import extract_resume_text, parse_resume_text
from app.schemas.resumes import ResumeParseResponse
from app.vectorstore.embeddings import deterministic_embedding

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("/parse", response_model=ResumeParseResponse)
async def parse_resume(file: Annotated[UploadFile, File()]) -> ResumeParseResponse:
    plain_text = await extract_resume_text(file)
    profile = parse_resume_text(plain_text)
    embedding = deterministic_embedding(" ".join(profile.keywords) or plain_text)
    return ResumeParseResponse(
        profile=profile,
        plain_text=plain_text,
        embedding=embedding,
        parser_version="local-heuristic-v1",
    )
