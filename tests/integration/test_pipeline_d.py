from __future__ import annotations

from pathlib import Path

from packages.model_runner.asr import MockASRAdapter
from packages.model_runner.mock import MockModelAdapter
from packages.pipeline_runner.pipeline_d import run_pipeline_d
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


def test_pipeline_d_runs_cascaded_asr_then_tool_call(tmp_path: Path) -> None:
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
    asr_adapter = MockASRAdapter()
    text_adapter = MockModelAdapter()

    records = run_pipeline_d(
        examples,
        run_id="smoke-004",
        asr_adapter=asr_adapter,
        text_adapter=text_adapter,
        registry=registry,
        executor=executor,
        output_path=tmp_path / "pipeline-d.jsonl",
    )

    assert len(records) == 1
    record = records[0]
    assert record.pipeline == "D"
    assert record.input_modality == "audio"
    assert record.transcript == "Convert 2 kilometers to meters."
    assert record.tool_execution_result is not None
    assert (tmp_path / "pipeline-d.jsonl").exists()


def test_pipeline_d_records_transcript_in_each_record(tmp_path: Path) -> None:
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
    asr_adapter = MockASRAdapter()
    text_adapter = MockModelAdapter()

    records = run_pipeline_d(
        examples,
        run_id="smoke-004",
        asr_adapter=asr_adapter,
        text_adapter=text_adapter,
        registry=registry,
        executor=executor,
    )

    record = records[0]
    assert record.transcript == "Hello there."
    assert record.tool_execution_result is None


def test_pipeline_d_uses_asr_override_transcript(tmp_path: Path) -> None:
    examples = [
        _audio_example(
            "v1-ru-0001-audio",
            "v1-ru-0001",
            "Convert 5 grams to kilograms.",
            tmp_path,
        ),
    ]
    registry = default_tool_registry()
    executor = ToolExecutor(registry)
    asr_adapter = MockASRAdapter(
        transcript_overrides={"v1-ru-0001-audio": "Convert 2 kilometers to meters."}
    )
    text_adapter = MockModelAdapter()

    records = run_pipeline_d(
        examples,
        run_id="smoke-004",
        asr_adapter=asr_adapter,
        text_adapter=text_adapter,
        registry=registry,
        executor=executor,
    )

    record = records[0]
    assert record.transcript == "Convert 2 kilometers to meters."
