from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResumeResponse(BaseModel):
    id: str
    original_filename: str
    file_mime_type: str
    file_size_bytes: int
    status: str
    active: bool
    parsed_profile: dict | None = None
    parser_version: str | None = None
    parse_error: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
