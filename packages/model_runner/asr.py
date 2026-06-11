from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

from packages.tts_synth.models import AudioExample


class ASRTranscript(BaseModel):
    """Raw ASR transcript metadata returned by an audio transcription adapter."""

    model_config = ConfigDict(extra="forbid")

    transcript: str
    adapter_name: str = Field(min_length=1)


@runtime_checkable
class ASRAdapter(Protocol):
    """Protocol for adapters that transcribe benchmark audio examples."""

    @property
    def name(self) -> str:
        """Return the stable adapter name stored in run artifacts."""
        ...

    def transcribe(self, audio: AudioExample) -> ASRTranscript:
        """Transcribe one audio benchmark example."""
        ...


class MockASRAdapter:
    """Deterministic ASR adapter for smoke tests and local benchmark runs."""

    name = "MockASRAdapter"

    def __init__(
        self,
        transcript_overrides: Mapping[str, str] | None = None,
    ) -> None:
        self.transcript_overrides = dict(transcript_overrides or {})

    def transcribe(self, audio: AudioExample) -> ASRTranscript:
        """Return the reference transcript unless an audio-specific override exists."""
        transcript = self.transcript_overrides.get(
            audio.audio_id,
            audio.reference_transcript,
        )
        return ASRTranscript(transcript=transcript, adapter_name=self.name)
