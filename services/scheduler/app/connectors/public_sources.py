from dataclasses import dataclass


SUPPORTED_PUBLIC_SOURCES = {"greenhouse", "lever", "ashby", "sample"}


@dataclass(frozen=True)
class DiscoveryTarget:
    source: str
    board_token: str | None = None
    company: str | None = None


def parse_discovery_targets(*, sources: str, board_tokens: str) -> list[DiscoveryTarget]:
    token_map = _parse_token_map(board_tokens)
    targets = []
    for source in [item.strip() for item in sources.split(",") if item.strip()]:
        if source not in SUPPORTED_PUBLIC_SOURCES:
            continue
        targets.append(DiscoveryTarget(source=source, board_token=token_map.get(source)))
    return targets


def _parse_token_map(value: str) -> dict[str, str]:
    token_map: dict[str, str] = {}
    for pair in [item.strip() for item in value.split(",") if item.strip()]:
        if ":" not in pair:
            continue
        source, token = pair.split(":", 1)
        token_map[source.strip()] = token.strip()
    return token_map
