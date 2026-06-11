import wave
from pathlib import Path

from packages.dataset_builder import read_jsonl as read_dataset_jsonl
from packages.tts_synth.models import SynthesisSettings
from packages.tts_synth.synthesizer import FixtureSynthesizer, synthesize_dataset


def test_fixture_synthesizer_writes_deterministic_silent_wav(tmp_path: Path) -> None:
    example = read_dataset_jsonl(Path("data/fixtures/examples.small.jsonl"))[0]
    settings = SynthesisSettings(
        engine="fixture-silent",
        sample_rate_hz=8_000,
        duration_ms=100,
    )
    synthesizer = FixtureSynthesizer(settings=settings)

    first = synthesizer.synthesize(example, tmp_path)
    first_bytes = Path(first.audio_path).read_bytes()
    second = synthesizer.synthesize(example, tmp_path)

    assert first == second
    assert Path(second.audio_path).read_bytes() == first_bytes
    assert first.audio_id == example.audio_id
    assert first.example_id == example.example_id
    assert first.split == example.split
    assert first.reference_transcript == example.text
    assert first.duration_ms == 100

    with wave.open(first.audio_path, "rb") as wav_file:
        assert wav_file.getframerate() == 8_000
        assert wav_file.getnchannels() == 1
        assert wav_file.getsampwidth() == 2
        assert wav_file.getnframes() == 800


def test_synthesize_dataset_creates_one_audio_record_per_example(
    tmp_path: Path,
) -> None:
    examples = read_dataset_jsonl(Path("data/fixtures/examples.small.jsonl"))

    records = synthesize_dataset(
        examples,
        output_dir=tmp_path,
        settings=SynthesisSettings(
            engine="fixture-silent",
            sample_rate_hz=16_000,
            duration_ms=10,
        ),
    )

    assert len(records) == len(examples)
    assert {record.example_id for record in records} == {
        example.example_id for example in examples
    }
    assert {record.audio_id for record in records} == {
        example.audio_id for example in examples
    }
    assert all(Path(record.audio_path).exists() for record in records)
