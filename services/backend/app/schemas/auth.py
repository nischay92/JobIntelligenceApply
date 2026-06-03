from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuthLoginResponse(BaseModel):
    authorization_url: str


class UserProfile(BaseModel):
    id: str
    email: str
    name: str
    avatar_url: str | None = None
    timezone: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
