from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class JobDiscoveryRequest(BaseModel):
    source: str = Field(pattern="^(greenhouse|lever|ashby|sample)$")
    board_token: str | None = None
    company: str | None = None
    limit: int = Field(default=25, ge=1, le=100)


class JobDiscoveryResponse(BaseModel):
    run_id: str
    status: str
    records_seen: int
    records_created: int
    records_updated: int


class JobResponse(BaseModel):
    id: str
    source: str
    external_id: str
    company: str
    title: str
    location: str | None = None
    employment_type: str | None = None
    description_url: str
    apply_url: str | None = None
    remote_policy: str
    status: str
    discovered_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
