from fastapi import FastAPI

from app.api.v1.health import router as health_router
from app.api.v1.resumes import router as resumes_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="ApplyWise AI Service",
        version="0.1.0",
        description="AI service skeleton for parsing, scoring, generation, and embeddings.",
    )
    app.include_router(health_router)
    app.include_router(resumes_router, prefix="/api/v1")
    return app


app = create_app()
