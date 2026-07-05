from pathlib import Path

from apps.cli.__main__ import app
from packages.dataset_builder.models import BenchmarkExample
from packages.tts_synth.io import read_jsonl
from packages.tts_synth.models import AudioExample, SynthesisSettings
from pytest import MonkeyPatch
from typer.testing import CliRunner


def test_audio_synthesize_cli_writes_audio_and_metadata(tmp_path: Path) -> None:
    dataset = Path("data/fixtures/examples.small.jsonl")
    output = tmp_path / "audio"
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "audio",
            "synthesize",
            "--dataset",
            str(dataset),
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 0, result.output
    metadata = output / "audio.jsonl"
    assert metadata.exists()
    records = read_jsonl(metadata)
    assert len(records) == 6
    assert all(Path(record.audio_path).exists() for record in records)
    assert records[0].reference_transcript == "Convert 2 kilometer to meter."
    assert "wrote 6 audio examples" in result.output


def test_audio_synthesize_cli_accepts_piper_options(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    dataset = Path("data/fixtures/examples.small.jsonl")
    output = tmp_path / "audio"
    model_path = tmp_path / "voice.onnx"
    config_path = tmp_path / "voice.onnx.json"
    model_path.write_bytes(b"model")
    config_path.write_text("{}", encoding="utf-8")

    def fake_synthesize_dataset(
        examples: list[BenchmarkExample],
        *,
        output_dir: Path,
        settings: SynthesisSettings,
    ) -> list[AudioExample]:
        output_dir.mkdir(parents=True, exist_ok=True)
        return [
            AudioExample.from_benchmark_example(
                examples[0],
                audio_path=output_dir / f"{examples[0].audio_id}.wav",
                settings=settings,
                duration_ms=100,
                voice=settings.voice,
            )
        ]

    monkeypatch.setattr("apps.cli.audio.synthesize_dataset", fake_synthesize_dataset)

    result = CliRunner().invoke(
        app,
        [
            "audio",
            "synthesize",
            "--dataset",
            str(dataset),
            "--output",
            str(output),
            "--engine",
            "piper",
            "--voice",
            "ru_RU-irina-medium",
            "--voice-model-path",
            str(model_path),
            "--voice-config-path",
            str(config_path),
        ],
    )

    assert result.exit_code == 0, result.output
    records = read_jsonl(output / "audio.jsonl")
    assert records[0].tts_engine == "piper"
    assert records[0].voice == "ru_RU-irina-medium"
    assert records[0].synthesis_settings.voice_model_path == model_path


def test_audio_synthesize_cli_does_not_write_manifest_on_failure(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    def fail_synthesis(*_args: object, **_kwargs: object) -> list[AudioExample]:
        raise RuntimeError("synthesis failed")

    monkeypatch.setattr("apps.cli.audio.synthesize_dataset", fail_synthesis)
    output = tmp_path / "audio"

    result = CliRunner().invoke(
        app,
        [
            "audio",
            "synthesize",
            "--dataset",
            "data/fixtures/examples.small.jsonl",
            "--output",
            str(output),
            "--engine",
            "piper",
            "--voice-model-path",
            str(tmp_path / "voice.onnx"),
        ],
    )

    assert result.exit_code != 0
    assert not (output / "audio.jsonl").exists()


def test_audio_synthesize_cli_reports_existing_output_collision(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    def fail_synthesis(*_args: object, **_kwargs: object) -> list[AudioExample]:
        raise RuntimeError("audio output already exists")

    monkeypatch.setattr("apps.cli.audio.synthesize_dataset", fail_synthesis)
    output = tmp_path / "audio"

    result = CliRunner().invoke(
        app,
        [
            "audio",
            "synthesize",
            "--dataset",
            "data/fixtures/examples.small.jsonl",
            "--output",
            str(output),
            "--engine",
            "piper",
            "--voice-model-path",
            str(tmp_path / "voice.onnx"),
        ],
    )

    assert result.exit_code != 0
    assert "audio output already exists" in result.output
