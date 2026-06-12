from __future__ import annotations

from typing import Any

import pytest
from packages.dataset_builder.models import BenchmarkExample
from packages.metrics.modality_gap import modality_gap, paired_example_ids
from packages.metrics.tool_use import evaluate_run
from packages.pipeline_runner.artifacts import PipelineRunRecord
from packages.tool_schema import ToolInvocation
from packages.tool_schema.models import ToolArguments, Unit


def _example(example_id: str) -> BenchmarkExample:
    return BenchmarkExample(
        example_id=example_id,
        dataset_version="v1",
        language="en",
        split="test",
        unit_family="length",
        text="Convert 2 kilometers to meters.",
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


def _parsed_output(*, value: float = 2) -> dict[str, Any]:
    return {
        "needs_tool": True,
        "tool_call": {
            "tool": "units.convert",
            "arguments": {
                "value": value,
                "from_unit": "kilometer",
                "to_unit": "meter",
            },
        },
        "final_answer": "2 kilometers is 2000 meters.",
    }


def _record(
    example_id: str,
    *,
    pipeline: str,
    input_modality: str,
    value: float = 2,
) -> PipelineRunRecord:
    return PipelineRunRecord(
        run_id="run-001",
        pipeline=pipeline,  # type: ignore[arg-type]
        example_id=example_id,
        dataset_version="v1",
        model_adapter="MockModelAdapter",
        input_modality=input_modality,  # type: ignore[arg-type]
        raw_output="{}",
        parsed_output=_parsed_output(value=value),
        first_pass_parsable=True,
        repair_attempted=False,
        repair_success=False,
    )


def test_paired_example_ids_uses_shared_ids_only() -> None:
    examples = [_example("e1"), _example("e2"), _example("e3")]
    text_evaluations = evaluate_run(
        [
            _record("e1", pipeline="A", input_modality="text"),
            _record("e2", pipeline="A", input_modality="text"),
        ],
        examples,
    )
    audio_evaluations = evaluate_run(
        [
            _record("e2", pipeline="B", input_modality="audio"),
            _record("e3", pipeline="B", input_modality="audio"),
        ],
        examples,
    )

    assert paired_example_ids(text_evaluations, audio_evaluations) == {"e2"}


def test_modality_gap_is_text_minus_audio_exact_match_over_pairs() -> None:
    examples = [_example("e1"), _example("e2"), _example("e3")]
    text_evaluations = evaluate_run(
        [
            _record("e1", pipeline="A", input_modality="text"),
            _record("e2", pipeline="A", input_modality="text"),
        ],
        examples,
    )
    audio_evaluations = evaluate_run(
        [
            _record("e1", pipeline="B", input_modality="audio"),
            _record("e2", pipeline="B", input_modality="audio", value=999),
            # e3 has no text counterpart and must not affect the gap.
            _record("e3", pipeline="B", input_modality="audio", value=999),
        ],
        examples,
    )

    gap = modality_gap(text_evaluations, audio_evaluations)

    # Paired ids e1/e2: text exact match 1.0, audio exact match 0.5.
    assert gap == pytest.approx(0.5)


def test_modality_gap_is_none_without_paired_examples() -> None:
    examples = [_example("e1"), _example("e2")]
    text_evaluations = evaluate_run(
        [_record("e1", pipeline="A", input_modality="text")],
        examples,
    )
    audio_evaluations = evaluate_run(
        [_record("e2", pipeline="B", input_modality="audio")],
        examples,
    )

    assert modality_gap(text_evaluations, audio_evaluations) is None


def test_modality_gap_is_zero_when_modalities_match() -> None:
    examples = [_example("e1")]
    text_evaluations = evaluate_run(
        [_record("e1", pipeline="A", input_modality="text")],
        examples,
    )
    audio_evaluations = evaluate_run(
        [_record("e1", pipeline="C", input_modality="audio")],
        examples,
    )

    assert modality_gap(text_evaluations, audio_evaluations) == pytest.approx(0.0)
