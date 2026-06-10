from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field


class ModelOutput(BaseModel):
    """Raw model response metadata returned by a model adapter."""

    model_config = ConfigDict(extra="forbid")

    raw_output: str = Field(min_length=1)
    adapter_name: str = Field(min_length=1)


@runtime_checkable
class TextModelAdapter(Protocol):
    """Protocol for adapters that turn text prompts into raw model output."""

    @property
    def name(self) -> str:
        """Return the stable adapter name stored in run artifacts."""
        ...

    def generate_text(self, prompt: str) -> ModelOutput:
        """Generate one raw model output for a text prompt."""
        ...
