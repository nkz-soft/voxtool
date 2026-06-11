from __future__ import annotations

import wave
from collections.abc import Iterable
from pathlib import Path

from packages.dataset_builder.models import BenchmarkExample
from packages.tts_synth.models import AudioExample, SynthesisSettings


class FixtureSynthesizer:
    """Create deterministic silent WAV fixtures for benchmark audio metadata."""

    def __init__(self, settings: SynthesisSettings | None = None) -> None:
        """Initialize the synthesizer with deterministic output settings."""
        self.settings = settings or SynthesisSettings()

    def synthesize(self, example: BenchmarkExample, output_dir: Path) -> AudioExample:
        """Write a silent WAV file and return linked audio metadata."""
        output_dir.mkdir(parents=True, exist_ok=True)
        audio_path = output_dir / f"{example.audio_id}.wav"
        frame_count = (self.settings.sample_rate_hz * self.settings.duration_ms) // 1000
        zero_frame = b"\x00" * self.settings.sample_width_bytes
        frames = zero_frame * frame_count * self.settings.channels

        with wave.open(str(audio_path), "wb") as wav_file:
            wav_file.setnchannels(self.settings.channels)
            wav_file.setsampwidth(self.settings.sample_width_bytes)
            wav_file.setframerate(self.settings.sample_rate_hz)
            wav_file.writeframes(frames)

        return AudioExample.from_benchmark_example(
            example,
            audio_path=audio_path,
            settings=self.settings,
            duration_ms=self.settings.duration_ms,
        )


def synthesize_dataset(
    examples: Iterable[BenchmarkExample],
    *,
    output_dir: Path,
    settings: SynthesisSettings | None = None,
) -> list[AudioExample]:
    """Synthesize one deterministic fixture audio record per benchmark example."""
    synthesizer = FixtureSynthesizer(settings=settings)
    return [synthesizer.synthesize(example, output_dir) for example in examples]
