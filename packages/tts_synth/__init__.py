"""Text-to-speech synthesis package."""

from typing import Any

from packages.tts_synth.models import AudioExample, SynthesisSettings

__all__ = [
    "AudioExample",
    "FixtureSynthesizer",
    "SynthesisSettings",
    "read_jsonl",
    "synthesize_dataset",
    "write_jsonl",
]


def __getattr__(name: str) -> Any:
    if name in {"FixtureSynthesizer", "synthesize_dataset"}:
        from packages.tts_synth.synthesizer import (
            FixtureSynthesizer,
            synthesize_dataset,
        )

        return {
            "FixtureSynthesizer": FixtureSynthesizer,
            "synthesize_dataset": synthesize_dataset,
        }[name]
    if name in {"read_jsonl", "write_jsonl"}:
        from packages.tts_synth.io import read_jsonl, write_jsonl

        return {"read_jsonl": read_jsonl, "write_jsonl": write_jsonl}[name]
    raise AttributeError(name)
