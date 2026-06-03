from pydantic import BaseModel, Field


class ParsedResumeProfile(BaseModel):
    skills: list[str] = Field(default_factory=list)
    experience: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)


class ResumeParseResponse(BaseModel):
    profile: ParsedResumeProfile
    plain_text: str
    embedding: list[float]
    parser_version: str
