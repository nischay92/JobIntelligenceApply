import secrets
from typing import Annotated
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.repositories.users import UserRepository
from app.schemas.auth import AuthLoginResponse, UserProfile

router = APIRouter(prefix="/auth", tags=["auth"])

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"


def _require_google_oauth_config() -> None:
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured.",
        )


@router.get("/google/login", response_model=AuthLoginResponse)
def google_login(request: Request) -> AuthLoginResponse:
    _require_google_oauth_config()
    state = secrets.token_urlsafe(32)
    request.session["oauth_state"] = state

    query = urlencode(
        {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "select_account",
        }
    )
    return AuthLoginResponse(authorization_url=f"{GOOGLE_AUTH_URL}?{query}")


@router.get("/google/callback")
async def google_callback(
    request: Request,
    code: str,
    state: str,
    db: Annotated[Session, Depends(get_db)],
) -> RedirectResponse:
    _require_google_oauth_config()
    expected_state = request.session.pop("oauth_state", None)
    if not expected_state or state != expected_state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth state.")

    async with httpx.AsyncClient(timeout=15) as client:
        token_response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
            headers={"Accept": "application/json"},
        )
        if token_response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google OAuth token exchange failed.",
            )

        access_token = token_response.json().get("access_token")
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google OAuth token response was missing an access token.",
            )

        profile_response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
        )
        if profile_response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google profile lookup failed.",
            )

    profile = profile_response.json()
    if not profile.get("sub") or not profile.get("email"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google profile response was missing required identity fields.",
        )

    user = UserRepository(db).upsert_google_user(
        google_sub=profile["sub"],
        email=profile["email"],
        name=profile.get("name") or profile["email"],
        avatar_url=profile.get("picture"),
    )
    request.session["user_id"] = user.id
    return RedirectResponse(f"{settings.frontend_url}/?auth=success", status_code=status.HTTP_302_FOUND)


@router.get("/me", response_model=UserProfile)
def me(request: Request, db: Annotated[Session, Depends(get_db)]) -> UserProfile:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")

    user = UserRepository(db).get_by_id(user_id)
    if user is None:
        request.session.clear()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")

    return UserProfile.model_validate(user)


@router.post("/logout")
def logout(request: Request) -> dict[str, str]:
    request.session.clear()
    return {"status": "ok"}
