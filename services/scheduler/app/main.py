import logging
import signal
import time

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger("applywise.scheduler")


def create_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone=settings.scheduler_timezone)

    if settings.scheduler_discovery_enabled:
        scheduler.add_job(
            lambda: logger.info("Discovery job placeholder executed."),
            "interval",
            hours=1,
            id="hourly_job_discovery",
            replace_existing=True,
        )

    if settings.scheduler_digests_enabled:
        scheduler.add_job(
            lambda: logger.info("Digest job placeholder executed."),
            "interval",
            hours=1,
            id="hourly_digest",
            replace_existing=True,
        )

    return scheduler


def main() -> None:
    scheduler = create_scheduler()
    stop_requested = False

    def request_stop(_signum: int, _frame: object) -> None:
        nonlocal stop_requested
        stop_requested = True

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)

    scheduler.start()
    logger.info("ApplyWise scheduler started.")

    try:
        while not stop_requested:
            time.sleep(1)
    finally:
        scheduler.shutdown(wait=False)
        logger.info("ApplyWise scheduler stopped.")


if __name__ == "__main__":
    main()

