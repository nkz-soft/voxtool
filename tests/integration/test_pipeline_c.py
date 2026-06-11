from __future__ import annotations

from pathlib import Path

from packages.model_runner.mock import MockModelAdapter
from packages.pipeline_runner.pipeline_c import run_pipeline_c
from packages.tool_schema.providers import ToolExecutor
from packages.tool_schema.units import default_tool_registry
from packages.tts_synth.models import AudioExample, SynthesisSettings


def _audio_example(
    audio_id: str,
    example_id: str,
    reference_transcript: str,
    tmp_path: Path,
) -> AudioExample:
    return AudioExample(
        audio_id=audio_id,
        example_id=example_id,
        dataset_version="v1",
        language="en",
        split="test",
        reference_transcript=reference_transcript,
        audio_path=str(tmp_path / f"{audio_id}.wav"),
        tts_engine="fixture-silent",
        voice="en-fixture",
        sample_rate_hz=16_000,
        duration_ms=250,
        synthesis_settings=SynthesisSettings(duration_ms=250),
    )


def test_pipeline_c_runs_audio_examples_with_tool_calls(tmp_path: Path) -> None:
    examples = [
        _audio_example(
            "v1-en-0001-audio",
            "v1-en-0001",
            "Convert 2 kilometers to meters.",
            tmp_path,
        ),
        _audio_example(
            "v1-en-0002-audio",
            "v1-en-0002",
            "Hello there.",
            tmp_path,
        ),
    ]
    registry = default_tool_registry()
    executor = ToolExecutor(registry)
    adapter = MockModelAdapter()

    records = run_pipeline_c(
        examples,
        run_id="smoke-003",
        model_adapter=adapter,
        registry=registry,
        executor=executor,
        output_path=tmp_path / "pipeline-c.jsonl",
    )

    assert len(records) == 2
    assert records[0].pipeline == "C"
    assert records[0].input_modality == "audio"
    assert records[0].raw_output != ""
    assert (tmp_path / "pipeline-c.jsonl").exists()


def test_pipeline_c_records_tool_execution_for_conversion(tmp_path: Path) -> None:
    examples = [
        _audio_example(
            "v1-en-0001-audio",
            "v1-en-0001",
            "Convert 2 kilometers to meters.",
            tmp_path,
        ),
    ]
    registry = default_tool_registry()
    executor = ToolExecutor(registry)
    adapter = MockModelAdapter()

    records = run_pipeline_c(
        examples,
        run_id="smoke-003",
        model_adapter=adapter,
        registry=registry,
        executor=executor,
    )

    record = records[0]
    assert record.tool_execution_result is not None
    assert record.tool_execution_result.failure is None


def test_pipeline_c_records_no_tool_when_not_needed(tmp_path: Path) -> None:
    examples = [
        _audio_example(
            "v1-en-0002-audio",
            "v1-en-0002",
            "Hello there.",
            tmp_path,
        ),
    ]
    registry = default_tool_registry()
    executor = ToolExecutor(registry)
    adapter = MockModelAdapter()

    records = run_pipeline_c(
        examples,
        run_id="smoke-003",
        model_adapter=adapter,
        registry=registry,
        executor=executor,
    )

    record = records[0]
    assert record.tool_execution_result is None
