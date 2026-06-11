from pathlib import Path

from apps.cli.__main__ import app
from packages.pipeline_runner.runner import run_benchmark
from packages.tool_schema.providers import ToolExecutor
from packages.tool_schema.units import default_tool_registry
from packages.tts_synth.io import write_jsonl
from packages.tts_synth.models import AudioExample, SynthesisSettings
from typer.testing import CliRunner


def _write_audio_metadata(path: Path) -> Path:
    record = AudioExample(
        audio_id="v1-en-length-0001-audio",
        example_id="v1-en-length-0001",
        dataset_version="v1",
        language="en",
        split="test",
        reference_transcript="Convert two kilometers to meters.",
        audio_path=str(path.parent / "v1-en-length-0001-audio.wav"),
        tts_engine="fixture-silent",
        voice="en-fixture",
        sample_rate_hz=16_000,
        duration_ms=250,
        synthesis_settings=SynthesisSettings(duration_ms=250),
    )
    write_jsonl(path, [record])
    return path


def test_runner_dispatches_pipeline_b_audio_metadata(tmp_path: Path) -> None:
    registry = default_tool_registry()
    metadata_path = _write_audio_metadata(tmp_path / "audio.jsonl")

    records = run_benchmark(
        pipeline="B",
        dataset_path=metadata_path,
        output_path=tmp_path / "pipeline-b.jsonl",
        run_id="smoke-003",
        registry=registry,
        executor=ToolExecutor(registry),
    )

    assert len(records) == 1
    assert records[0].pipeline == "B"
    assert records[0].wer == 0


def test_benchmark_cli_runs_pipeline_b_with_audio_metadata(tmp_path: Path) -> None:
    metadata_path = _write_audio_metadata(tmp_path / "audio.jsonl")
    output_path = tmp_path / "pipeline-b.jsonl"
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "benchmark",
            "run",
            "--audio-metadata",
            str(metadata_path),
            "--output",
            str(output_path),
            "--run-id",
            "smoke-004",
            "--pipeline",
            "B",
        ],
    )

    assert result.exit_code == 0, result.output
    assert output_path.exists()
    assert "wrote 1 Pipeline B records" in result.output
