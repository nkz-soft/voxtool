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


def test_synthesis_settings_accepts_piper_voice_resources() -> None:
    settings = SynthesisSettings(
        engine="piper",
        voice="ru_RU-irina-medium",
        voice_model_path=Path("model-files/piper/ru_RU-irina-medium.onnx"),
        voice_config_path=Path("model-files/piper/ru_RU-irina-medium.onnx.json"),
        voice_by_language={"ru": "ru_RU-irina-medium", "en": "en_US-lessac-medium"},
        voice_model_path_by_language={
            "ru": Path("model-files/piper/ru_RU-irina-medium.onnx"),
            "en": Path("model-files/piper/en_US-lessac-medium.onnx"),
        },
        voice_config_path_by_language={
            "ru": Path("model-files/piper/ru_RU-irina-medium.onnx.json"),
            "en": Path("model-files/piper/en_US-lessac-medium.onnx.json"),
        },
        sentence_silence=0.2,
        length_scale=1.0,
        noise_scale=0.667,
        noise_w_scale=0.8,
    )

    payload = settings.model_dump(mode="json")

    assert payload["engine"] == "piper"
    assert payload["voice"] == "ru_RU-irina-medium"
    assert payload["voice_by_language"]["en"] == "en_US-lessac-medium"
    assert payload["voice_model_path"].endswith("ru_RU-irina-medium.onnx")


def test_piper_audio_metadata_round_trip_preserves_voice_fields(tmp_path: Path) -> None:
    settings = SynthesisSettings(
        engine="piper",
        voice="ru_RU-irina-medium",
        voice_model_path=Path("model-files/piper/ru_RU-irina-medium.onnx"),
        voice_config_path=Path("model-files/piper/ru_RU-irina-medium.onnx.json"),
    )
    audio = AudioExample(
        audio_id="v1-ru-length-0001-audio",
        example_id="v1-ru-length-0001",
        dataset_version="v1",
        language="ru",
        split="validation",
        reference_transcript="Переведи 2 километра в метры.",
        audio_path="audio/v1-ru-length-0001-audio.wav",
        tts_engine="piper",
        voice="ru_RU-irina-medium",
        sample_rate_hz=22_050,
        duration_ms=640,
        synthesis_settings=settings,
    )
    output = tmp_path / "audio.jsonl"

    write_jsonl(output, [audio])
    loaded = read_jsonl(output)

    assert loaded == [audio]
    assert loaded[0].synthesis_settings.voice == "ru_RU-irina-medium"
    assert loaded[0].synthesis_settings.engine == "piper"


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
