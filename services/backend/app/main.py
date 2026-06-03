from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="ApplyWise AI Backend API",
        version="0.1.0",
        description="Backend API skeleton for ApplyWise AI.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.session_secret,
        session_cookie=settings.session_cookie_name,
        max_age=settings.session_max_age_seconds,
        same_site="lax",
        https_only=settings.app_env == "production",
    )

    app.include_router(health_router)
    app.include_router(auth_router, prefix="/api/v1")
    return app


app = create_app()
