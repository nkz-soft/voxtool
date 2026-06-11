from __future__ import annotations

import pytest
from packages.model_runner.gemma3n import Gemma3nAdapter
from packages.tts_synth.models import AudioExample, SynthesisSettings


def _audio_example(audio_id: str = "v1-en-0001-audio") -> AudioExample:
    return AudioExample(
        audio_id=audio_id,
        example_id="v1-en-0001",
        dataset_version="v1",
        language="en",
        split="test",
        reference_transcript="Convert two kilometers to meters.",
        audio_path=f"/tmp/{audio_id}.wav",
        tts_engine="fixture-silent",
        voice="en-fixture",
        sample_rate_hz=16_000,
        duration_ms=250,
        synthesis_settings=SynthesisSettings(duration_ms=250),
    )


def test_gemma3n_adapter_has_stable_name() -> None:
    adapter = Gemma3nAdapter()

    assert adapter.name == "Gemma3nAdapter"


def test_gemma3n_adapter_raises_not_implemented_on_generate_audio() -> None:
    adapter = Gemma3nAdapter()

    with pytest.raises(NotImplementedError):
        adapter.generate_audio(_audio_example())


def test_gemma3n_adapter_is_a_placeholder_for_manual_runs() -> None:
    doc = (Gemma3nAdapter.__doc__ or "").lower()

    assert "manual" in doc or "placeholder" in doc
