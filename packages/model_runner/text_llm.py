from __future__ import annotations

from packages.model_runner.base import ModelOutput


class TextLLMAdapter:
    """Placeholder interface for future transcript-to-tool LLM adapters."""

    name = "TextLLMAdapter"

    def generate_text(self, prompt: str) -> ModelOutput:
        """Generate text model output for manual experiments when implemented."""
        raise NotImplementedError(
            "TextLLMAdapter is a placeholder for manual transcript-to-tool runs."
        )
