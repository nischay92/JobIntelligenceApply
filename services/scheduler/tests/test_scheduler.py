from app.main import create_scheduler
from app.connectors.public_sources import parse_discovery_targets


def test_scheduler_can_be_created() -> None:
    scheduler = create_scheduler()

    assert scheduler.timezone is not None


def test_parse_discovery_targets() -> None:
    targets = parse_discovery_targets(
        sources="greenhouse,lever,unknown",
        board_tokens="greenhouse:openai,lever:stripe",
    )

    assert [target.source for target in targets] == ["greenhouse", "lever"]
    assert targets[0].board_token == "openai"
