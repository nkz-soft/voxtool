from __future__ import annotations

from pathlib import Path

import pytest
from packages.dataset_builder.models import BenchmarkExample
from packages.model_runner.asr import MockASRAdapter
from packages.model_runner.mock import MockModelAdapter
from packages.pipeline_runner.pipeline_a import run_pipeline_a
from packages.pipeline_runner.pipeline_b import run_pipeline_b
from packages.pipeline_runner.pipeline_c import run_pipeline_c
from packages.pipeline_runner.pipeline_d import run_pipeline_d
from packages.tool_schema import ToolInvocation, ToolRegistry
from packages.tool_schema.models import ToolArguments, Unit
from packages.tool_schema.providers import ToolExecutor
from packages.tool_schema.units import default_tool_registry
from packages.tts_synth.models import AudioExample, SynthesisSettings


def _text_example(example_id: str, text: str) -> BenchmarkExample:
    return BenchmarkExample(
        example_id=example_id,
        dataset_version="v1",
        language="en",
        split="test",
        unit_family="length",
        text=text,
        needs_tool=True,
        expected_tool_call=ToolInvocation(
            tool="units.convert",
            arguments=ToolArguments(
                value=2,
                from_unit=Unit.KILOMETER,
                to_unit=Unit.METER,
            ),
        ),
        expected_final_answer="2 kilometers is 2000 meters.",
        audio_id=f"{example_id}-audio",
    )


def _audio_example(
    audio_id: str,
    example_id: str,
    transcript: str,
    tmp_path: Path,
) -> AudioExample:
    return AudioExample(
        audio_id=audio_id,
        example_id=example_id,
        dataset_version="v1",
        language="en",
        split="test",
        reference_transcript=transcript,
        audio_path=str(tmp_path / f"{audio_id}.wav"),
        tts_engine="fixture-silent",
        voice="en-fixture",
        sample_rate_hz=16_000,
        duration_ms=250,
        synthesis_settings=SynthesisSettings(duration_ms=250),
    )


@pytest.fixture()
def registry() -> ToolRegistry:
    return default_tool_registry()


@pytest.fixture()
def executor(registry: ToolRegistry) -> ToolExecutor:
    return ToolExecutor(registry)


def test_all_pipelines_smoke(
    tmp_path: Path,
    registry: ToolRegistry,
    executor: ToolExecutor,
) -> None:
    text_examples = [
        _text_example("v1-en-0001", "Convert 2 kilometers to meters."),
    ]
    audio_examples = [
        _audio_example(
            "v1-en-0001-audio",
            "v1-en-0001",
            "Convert 2 kilometers to meters.",
            tmp_path,
        ),
    ]
    mock_model = MockModelAdapter()
    mock_asr = MockASRAdapter()

    records_a = run_pipeline_a(
        text_examples,
        run_id="smoke-all",
        model_adapter=mock_model,
        registry=registry,
        executor=executor,
        output_path=tmp_path / "pipeline-a.jsonl",
    )
    records_b = run_pipeline_b(
        audio_examples,
        run_id="smoke-all",
        asr_adapter=mock_asr,
        output_path=tmp_path / "pipeline-b.jsonl",
    )
    records_c = run_pipeline_c(
        audio_examples,
        run_id="smoke-all",
        model_adapter=mock_model,
        registry=registry,
        executor=executor,
        output_path=tmp_path / "pipeline-c.jsonl",
    )
    records_d = run_pipeline_d(
        audio_examples,
        run_id="smoke-all",
        asr_adapter=mock_asr,
        text_adapter=mock_model,
        registry=registry,
        executor=executor,
        output_path=tmp_path / "pipeline-d.jsonl",
    )

    assert records_a[0].pipeline == "A"
    assert records_b[0].pipeline == "B"
    assert records_c[0].pipeline == "C"
    assert records_d[0].pipeline == "D"

    pipelines = [
        ("A", records_a),
        ("B", records_b),
        ("C", records_c),
        ("D", records_d),
    ]
    for pipeline_letter, records in pipelines:
        assert len(records) == 1
        assert (tmp_path / f"pipeline-{pipeline_letter.lower()}.jsonl").exists()
