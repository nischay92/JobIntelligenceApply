from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.jobs import JobResponse


class ScoreJobsRequest(BaseModel):
    resume_id: str | None = None
    job_ids: list[str] = Field(default_factory=list)


class ScoreJobsResponse(BaseModel):
    status: str
    scored_count: int


class JobMatchResponse(BaseModel):
    id: str
    user_id: str
    resume_id: str
    job_id: str
    overall_score: int
    skill_score: int
    experience_score: int
    education_score: int
    missing_skills: list[str]
    missing_keywords: list[str]
    match_reasons: list[str]
    priority: str
    priority_reason: str
    scoring_model: str
    created_at: datetime
    updated_at: datetime
    job: JobResponse | None = None

    model_config = ConfigDict(from_attributes=True)
