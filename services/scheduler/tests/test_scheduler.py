from app.main import create_scheduler


def test_scheduler_can_be_created() -> None:
    scheduler = create_scheduler()

    assert scheduler.timezone is not None

