import logging

import httpx

from app.connectors.public_sources import parse_discovery_targets
from app.core.config import settings

logger = logging.getLogger("applywise.scheduler.discovery")


async def run_hourly_discovery() -> None:
    targets = parse_discovery_targets(
        sources=settings.discovery_sources,
        board_tokens=settings.discovery_board_tokens,
    )
    if not targets:
        logger.info("No public discovery targets configured.")
        return

    async with httpx.AsyncClient(timeout=60) as client:
        for target in targets:
            response = await client.post(
                f"{settings.backend_api_url}/internal/v1/jobs/discovery-runs",
                json={
                    "source": target.source,
                    "board_token": target.board_token,
                    "company": target.company,
                    "limit": 25,
                },
            )
            response.raise_for_status()
            logger.info("Discovery run completed for %s: %s", target.source, response.json())
