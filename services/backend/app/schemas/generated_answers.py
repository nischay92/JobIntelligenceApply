from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.jobs import JobResponse

ContentType = Literal[
    "resume_suggestions",
    "missing_keywords",
    "cover_letter",
    "recruiter_email",
    "linkedin_message",
    "why_company",
    "tell_me_about_yourself",
    "why_fit",
    "relevant_experience_summary",
]


class GenerateAnswerRequest(BaseModel):
    resume_id: str | None = None
    job_id: str
    content_type: ContentType
    prompt_label: str | None = None


class UpdateGeneratedAnswerRequest(BaseModel):
    content: str | None = None
    status: Literal["draft", "approved", "archived"] | None = None


class GeneratedAnswerResponse(BaseModel):
    id: str
    user_id: str
    resume_id: str
    job_id: str
    content_type: str
    prompt_label: str | None
    content: str
    extra_metadata: dict | None = Field(default=None)
    status: str
    vector_id: str | None
    created_at: datetime
    updated_at: datetime
    job: JobResponse | None = None

    model_config = ConfigDict(from_attributes=True)
