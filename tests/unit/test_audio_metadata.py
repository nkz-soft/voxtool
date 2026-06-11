import json
from pathlib import Path

import pytest
from packages.dataset_builder import read_jsonl as read_dataset_jsonl
from packages.tts_synth.io import read_jsonl, write_jsonl
from packages.tts_synth.models import AudioExample, SynthesisSettings
from pydantic import ValidationError


def test_audio_example_preserves_dataset_linkage_and_settings() -> None:
    """Audio metadata records keep the fields needed to pair text and audio."""
    settings = SynthesisSettings(engine="fixture-silent", sample_rate_hz=16_000)
    audio = AudioExample(
        audio_id="v1-en-length-0001-audio",
        example_id="v1-en-length-0001",
        dataset_version="v1",
        language="en",
        split="train",
        reference_transcript="Convert 2 kilometer to meter.",
        audio_path="audio/v1-en-length-0001-audio.wav",
        tts_engine="fixture-silent",
        voice="en-fixture",
        sample_rate_hz=16_000,
        duration_ms=1000,
        synthesis_settings=settings,
    )

    payload = audio.model_dump(mode="json")

    assert payload["audio_id"] == "v1-en-length-0001-audio"
    assert payload["example_id"] == "v1-en-length-0001"
    assert payload["split"] == "train"
    assert payload["reference_transcript"] == "Convert 2 kilometer to meter."
    assert payload["synthesis_settings"]["engine"] == "fixture-silent"


def test_audio_example_rejects_invalid_sample_rate() -> None:
    with pytest.raises(ValidationError):
        AudioExample(
            audio_id="audio-1",
            example_id="example-1",
            dataset_version="v1",
            language="en",
            split="train",
            reference_transcript="hello",
            audio_path="audio/audio-1.wav",
            tts_engine="fixture-silent",
            sample_rate_hz=0,
            synthesis_settings=SynthesisSettings(
                engine="fixture-silent",
                sample_rate_hz=0,
            ),
        )


def test_audio_metadata_jsonl_round_trip(tmp_path: Path) -> None:
    examples = read_dataset_jsonl(Path("data/fixtures/examples.small.jsonl"))
    records = [
        AudioExample.from_benchmark_example(
            example,
            audio_path=Path("audio") / f"{example.audio_id}.wav",
            settings=SynthesisSettings(
                engine="fixture-silent",
                sample_rate_hz=16_000,
                duration_ms=250,
            ),
            duration_ms=250,
        )
        for example in examples
    ]
    output = tmp_path / "audio.jsonl"

    count = write_jsonl(output, records)
    loaded = read_jsonl(output)

    assert count == len(examples)
    assert loaded == records
    first_line = output.read_text(encoding="utf-8").splitlines()[0]
    assert json.loads(first_line)["audio_id"] == examples[0].audio_id
