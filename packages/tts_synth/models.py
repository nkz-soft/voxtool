from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from packages.dataset_builder.models import BenchmarkExample, Language, Split


class SynthesisSettings(BaseModel):
    """Describe text-to-speech settings for benchmark audio generation."""

    model_config = ConfigDict(extra="forbid")

    engine: str = Field(default="fixture-silent", min_length=1)
    sample_rate_hz: int = Field(default=16_000, gt=0)
    duration_ms: int = Field(default=1000, gt=0)
    channels: int = Field(default=1, gt=0)
    sample_width_bytes: int = Field(default=2, gt=0)
    voice: str | None = None
    voice_model_path: Path | None = None
    voice_config_path: Path | None = None
    voice_by_language: dict[Language, str] = Field(default_factory=dict)
    voice_model_path_by_language: dict[Language, Path] = Field(default_factory=dict)
    voice_config_path_by_language: dict[Language, Path] = Field(default_factory=dict)
    sentence_silence: float | None = Field(default=None, ge=0)
    length_scale: float | None = Field(default=None, gt=0)
    noise_scale: float | None = Field(default=None, ge=0)
    noise_w_scale: float | None = Field(default=None, ge=0)


def piper_settings_from_environment() -> SynthesisSettings:
    """Build default Piper settings from documented local environment variables."""
    env = os.environ

    def optional_path(name: str) -> Path | None:
        value = env.get(name)
        return Path(value) if value else None

    voice_by_language: dict[Language, str] = {}
    voice_model_path_by_language: dict[Language, Path] = {}
    voice_config_path_by_language: dict[Language, Path] = {}

    en_voice = env.get("VOXTOOL_PIPER_VOICE_EN")
    if en_voice:
        voice_by_language["en"] = en_voice
    ru_voice = env.get("VOXTOOL_PIPER_VOICE_RU")
    if ru_voice:
        voice_by_language["ru"] = ru_voice

    en_model = optional_path("VOXTOOL_PIPER_VOICE_MODEL_EN")
    if en_model is not None:
        voice_model_path_by_language["en"] = en_model
    ru_model = optional_path("VOXTOOL_PIPER_VOICE_MODEL_RU")
    if ru_model is not None:
        voice_model_path_by_language["ru"] = ru_model

    en_config = optional_path("VOXTOOL_PIPER_VOICE_CONFIG_EN")
    if en_config is not None:
        voice_config_path_by_language["en"] = en_config
    ru_config = optional_path("VOXTOOL_PIPER_VOICE_CONFIG_RU")
    if ru_config is not None:
        voice_config_path_by_language["ru"] = ru_config

    return SynthesisSettings(
        engine="piper",
        voice=env.get("VOXTOOL_PIPER_VOICE"),
        voice_model_path=optional_path("VOXTOOL_PIPER_VOICE_MODEL"),
        voice_config_path=optional_path("VOXTOOL_PIPER_VOICE_CONFIG"),
        voice_by_language=voice_by_language,
        voice_model_path_by_language=voice_model_path_by_language,
        voice_config_path_by_language=voice_config_path_by_language,
    )


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
            voice=voice or settings.voice or f"{example.language}-fixture",
            sample_rate_hz=settings.sample_rate_hz,
            duration_ms=duration_ms,
            synthesis_settings=settings,
        )
