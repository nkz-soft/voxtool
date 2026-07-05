import wave
from pathlib import Path

import pytest
from packages.dataset_builder import read_jsonl as read_dataset_jsonl
from packages.tts_synth.models import SynthesisSettings
from packages.tts_synth.synthesizer import (
    FixtureSynthesizer,
    PiperSynthesizer,
    SynthesisError,
    SynthesisResourceError,
    synthesize_dataset,
)


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


def test_synthesize_dataset_selects_fixture_backend(tmp_path: Path) -> None:
    example = read_dataset_jsonl(Path("data/fixtures/examples.small.jsonl"))[0]

    records = synthesize_dataset(
        [example],
        output_dir=tmp_path,
        settings=SynthesisSettings(engine="fixture-silent", duration_ms=10),
    )

    assert records[0].tts_engine == "fixture-silent"
    assert records[0].voice == "en-fixture"


def test_synthesize_dataset_rejects_unknown_engine(tmp_path: Path) -> None:
    example = read_dataset_jsonl(Path("data/fixtures/examples.small.jsonl"))[0]

    with pytest.raises(SynthesisError, match="Unsupported TTS engine"):
        synthesize_dataset(
            [example],
            output_dir=tmp_path,
            settings=SynthesisSettings(engine="unknown"),
        )


def test_piper_synthesizer_writes_wav_and_metadata_with_mock_voice(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    model_path = tmp_path / "voice.onnx"
    config_path = tmp_path / "voice.onnx.json"
    model_path.write_bytes(b"model")
    config_path.write_text("{}", encoding="utf-8")
    example = read_dataset_jsonl(Path("data/fixtures/examples.small.jsonl"))[0]

    class FakeVoice:
        config = {"audio": {"sample_rate": 22_050}}

        def synthesize_wav(
            self, text: str, wav_file: wave.Wave_write, **_kwargs: object
        ) -> None:
            assert text == example.text
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(22_050)
            wav_file.writeframes(b"\x01\x00" * 2205)

    monkeypatch.setattr(
        "packages.tts_synth.synthesizer._load_piper_voice",
        lambda _model_path, config_path=None: FakeVoice(),
    )

    record = PiperSynthesizer(
        settings=SynthesisSettings(
            engine="piper",
            voice="test-voice",
            voice_model_path=model_path,
            voice_config_path=config_path,
        )
    ).synthesize(example, tmp_path)

    assert Path(record.audio_path).exists()
    assert record.tts_engine == "piper"
    assert record.voice == "test-voice"
    assert record.sample_rate_hz == 22_050
    assert record.duration_ms == 100
    assert record.example_id == example.example_id


def test_piper_metadata_is_deterministic_with_mock_voice(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    model_path = tmp_path / "voice.onnx"
    config_path = tmp_path / "voice.onnx.json"
    model_path.write_bytes(b"model")
    config_path.write_text("{}", encoding="utf-8")
    example = read_dataset_jsonl(Path("data/fixtures/examples.small.jsonl"))[0]

    class FakeVoice:
        def synthesize_wav(
            self, _text: str, wav_file: wave.Wave_write, **_kwargs: object
        ) -> None:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16_000)
            wav_file.writeframes(b"\x00\x00" * 160)

    monkeypatch.setattr(
        "packages.tts_synth.synthesizer._load_piper_voice",
        lambda _model_path, config_path=None: FakeVoice(),
    )
    settings = SynthesisSettings(
        engine="piper",
        voice="test-voice",
        voice_model_path=model_path,
        voice_config_path=config_path,
    )

    first = synthesize_dataset(
        [example], output_dir=tmp_path / "first", settings=settings
    )
    second = synthesize_dataset(
        [example], output_dir=tmp_path / "second", settings=settings
    )

    assert first[0].model_dump(exclude={"audio_path"}) == second[0].model_dump(
        exclude={"audio_path"}
    )


def test_piper_missing_dependency_is_clear(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    model_path = tmp_path / "voice.onnx"
    config_path = tmp_path / "voice.onnx.json"
    model_path.write_bytes(b"model")
    config_path.write_text("{}", encoding="utf-8")
    example = read_dataset_jsonl(Path("data/fixtures/examples.small.jsonl"))[0]

    def fail_load(_model_path: Path, config_path: Path | None = None) -> object:
        raise SynthesisResourceError("piper-tts is not installed")

    monkeypatch.setattr("packages.tts_synth.synthesizer._load_piper_voice", fail_load)

    with pytest.raises(SynthesisResourceError, match="piper-tts is not installed"):
        synthesize_dataset(
            [example],
            output_dir=tmp_path / "audio",
            settings=SynthesisSettings(
                engine="piper",
                voice_model_path=model_path,
                voice_config_path=config_path,
            ),
        )


def test_piper_missing_voice_files_fail_before_synthesis(tmp_path: Path) -> None:
    example = read_dataset_jsonl(Path("data/fixtures/examples.small.jsonl"))[0]

    with pytest.raises(SynthesisResourceError, match="Piper voice model not found"):
        synthesize_dataset(
            [example],
            output_dir=tmp_path,
            settings=SynthesisSettings(
                engine="piper",
                voice_model_path=tmp_path / "missing.onnx",
                voice_config_path=tmp_path / "missing.onnx.json",
            ),
        )


def test_piper_rejects_blank_text_and_duplicate_audio_paths(tmp_path: Path) -> None:
    examples = read_dataset_jsonl(Path("data/fixtures/examples.small.jsonl"))
    blank = examples[0].model_copy(update={"text": "   "})
    duplicate = examples[1].model_copy(update={"audio_id": examples[0].audio_id})
    settings = SynthesisSettings(
        engine="piper", voice_model_path=tmp_path / "voice.onnx"
    )

    with pytest.raises(SynthesisError, match="blank text"):
        synthesize_dataset([blank], output_dir=tmp_path, settings=settings)

    with pytest.raises(SynthesisError, match="Duplicate audio output path"):
        synthesize_dataset(
            [examples[0], duplicate], output_dir=tmp_path, settings=settings
        )


def test_piper_rejects_existing_output_collision(tmp_path: Path) -> None:
    example = read_dataset_jsonl(Path("data/fixtures/examples.small.jsonl"))[0]
    output = tmp_path / f"{example.audio_id}.wav"
    output.write_bytes(b"existing")

    with pytest.raises(SynthesisError, match="already exists"):
        synthesize_dataset(
            [example],
            output_dir=tmp_path,
            settings=SynthesisSettings(
                engine="piper",
                voice_model_path=tmp_path / "voice.onnx",
            ),
        )
