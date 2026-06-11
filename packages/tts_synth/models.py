from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from packages.dataset_builder.models import BenchmarkExample, Language, Split


class SynthesisSettings(BaseModel):
    """Describe deterministic text-to-speech settings for audio generation."""

    model_config = ConfigDict(extra="forbid")

    engine: str = Field(default="fixture-silent", min_length=1)
    sample_rate_hz: int = Field(default=16_000, gt=0)
    duration_ms: int = Field(default=1000, gt=0)
    channels: int = Field(default=1, gt=0)
    sample_width_bytes: int = Field(default=2, gt=0)


class AudioExample(BaseModel):
    """Represent one synthesized audio artifact linked to a text example."""

    model_config = ConfigDict(extra="forbid")

    audio_id: str = Field(min_length=1)
    example_id: str = Field(min_length=1)
    dataset_version: str = Field(min_length=1)
    language: Language
    split: Split
    reference_transcript: str = Field(min_length=1)
    audio_path: str = Field(min_length=1)
    tts_engine: str = Field(min_length=1)
    voice: str | None = None
    sample_rate_hz: int = Field(gt=0)
    duration_ms: int | None = Field(default=None, gt=0)
    synthesis_settings: SynthesisSettings

    @classmethod
    def from_benchmark_example(
        cls,
        example: BenchmarkExample,
        *,
        audio_path: Path,
        settings: SynthesisSettings,
        duration_ms: int | None = None,
        voice: str | None = None,
    ) -> AudioExample:
        """Build audio metadata from a benchmark text example."""
        return cls(
            audio_id=example.audio_id,
            example_id=example.example_id,
            dataset_version=example.dataset_version,
            language=example.language,
            split=example.split,
            reference_transcript=example.text,
            audio_path=str(audio_path),
            tts_engine=settings.engine,
            voice=voice or f"{example.language}-fixture",
            sample_rate_hz=settings.sample_rate_hz,
            duration_ms=duration_ms,
            synthesis_settings=settings,
        )
