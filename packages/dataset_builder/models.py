from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from packages.tool_schema import ToolInvocation

Language = Literal["en", "ru"]
Split = Literal["train", "validation", "test"]
DatasetUnitFamily = Literal["length", "mass", "temperature", "none"]


class GenerationMetadata(BaseModel):
    """Describe deterministic settings used to generate a dataset version."""

    model_config = ConfigDict(extra="forbid")

    dataset_version: str = Field(min_length=1)
    total_examples: int
    languages: list[Language]
    no_tool_ratio: float
    split_ratios: dict[Split, float]


class BenchmarkExample(BaseModel):
    """Represent one text benchmark example and its expected tool behavior."""

    model_config = ConfigDict(extra="forbid")

    example_id: str = Field(min_length=1)
    dataset_version: str = Field(min_length=1)
    language: Language
    split: Split
    unit_family: DatasetUnitFamily
    text: str = Field(min_length=1)
    needs_tool: bool
    expected_tool_call: ToolInvocation | None
    expected_final_answer: str = Field(min_length=1)
    audio_id: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_expected_tool_call(self) -> BenchmarkExample:
        """Reject records whose tool expectation contradicts the label."""
        if self.needs_tool and self.expected_tool_call is None:
            raise ValueError("expected_tool_call is required when needs_tool is true")
        if not self.needs_tool and self.expected_tool_call is not None:
            raise ValueError("expected_tool_call must be null when needs_tool is false")
        if not self.needs_tool and self.unit_family != "none":
            raise ValueError("unit_family must be none when needs_tool is false")
        return self
