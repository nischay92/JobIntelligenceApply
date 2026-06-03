from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.jobs import JobRepository, ProcessingRunRepository
from app.schemas.jobs import JobDiscoveryRequest, JobDiscoveryResponse
from app.services.job_connectors import get_connector


async def run_discovery(db: Session, request: JobDiscoveryRequest) -> JobDiscoveryResponse:
    run_repository = ProcessingRunRepository(db)
    run = run_repository.create(
        run_type="discovery",
        source=request.source,
        metadata=request.model_dump(),
    )

    try:
        connector = get_connector(request.source)
        discovered = await connector.discover(
            board_token=request.board_token,
            company=request.company,
            limit=request.limit,
        )
        created, updated = JobRepository(db).upsert_many(discovered)
        run_repository.finish(
            run,
            status="succeeded",
            records_seen=len(discovered),
            records_created=created,
            records_updated=updated,
        )
        return JobDiscoveryResponse(
            run_id=run.id,
            status="succeeded",
            records_seen=len(discovered),
            records_created=created,
            records_updated=updated,
        )
    except ValueError as exc:
        run_repository.finish(
            run,
            status="failed",
            records_seen=0,
            records_created=0,
            records_updated=0,
            error=str(exc),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        run_repository.finish(
            run,
            status="failed",
            records_seen=0,
            records_created=0,
            records_updated=0,
            error=str(exc),
        )
        raise
