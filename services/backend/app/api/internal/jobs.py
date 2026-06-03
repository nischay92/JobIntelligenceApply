from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.jobs import JobDiscoveryRequest, JobDiscoveryResponse
from app.services.job_discovery import run_discovery

router = APIRouter(prefix="/jobs", tags=["internal-jobs"])


@router.post("/discovery-runs", response_model=JobDiscoveryResponse, status_code=201)
async def create_internal_discovery_run(
    request: JobDiscoveryRequest,
    db: Annotated[Session, Depends(get_db)],
) -> JobDiscoveryResponse:
    return await run_discovery(db, request)
