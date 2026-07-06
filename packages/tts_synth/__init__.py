"""Public helpers for benchmark input audio synthesis and metadata."""

from typing import Any

from packages.tts_synth.models import AudioExample, SynthesisSettings

__all__ = [
    "AudioExample",
    "FixtureSynthesizer",
    "PiperSynthesizer",
    "SynthesisSettings",
    "SynthesisError",
    "SynthesisResourceError",
    "piper_settings_from_environment",
    "read_jsonl",
    "synthesize_dataset",
    "write_jsonl",
]


def __getattr__(name: str) -> Any:
    if name in {
        "FixtureSynthesizer",
        "PiperSynthesizer",
        "SynthesisError",
        "SynthesisResourceError",
        "synthesize_dataset",
    }:
        from packages.tts_synth.synthesizer import (
            FixtureSynthesizer,
            PiperSynthesizer,
            SynthesisError,
            SynthesisResourceError,
            synthesize_dataset,
        )

        return {
            "FixtureSynthesizer": FixtureSynthesizer,
            "PiperSynthesizer": PiperSynthesizer,
            "SynthesisError": SynthesisError,
            "SynthesisResourceError": SynthesisResourceError,
            "synthesize_dataset": synthesize_dataset,
        }[name]
    if name == "piper_settings_from_environment":
        from packages.tts_synth.models import piper_settings_from_environment

        return piper_settings_from_environment
    if name in {"read_jsonl", "write_jsonl"}:
        from packages.tts_synth.io import read_jsonl, write_jsonl

        return {"read_jsonl": read_jsonl, "write_jsonl": write_jsonl}[name]
    raise AttributeError(name)
