from typing import Protocol


class LLMProvider(Protocol):
    def generate(self, prompt: str, *, schema: dict | None = None) -> str:
        """Generate structured or unstructured text from a prompt."""

    def embed(self, text: str) -> list[float]:
        """Generate an embedding for semantic search."""

