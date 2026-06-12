from __future__ import annotations

from typing import Any

import pytest
from packages.dataset_builder.models import BenchmarkExample
from packages.metrics.tool_use import (
    confusion_matrix,
    evaluate_run,
    false_alarm_rate,
    parsability_rate,
    precision,
    recall,
    repair_success_rate,
    tool_decision_accuracy,
)
from packages.pipeline_runner.artifacts import PipelineRunRecord
from packages.tool_schema import ToolInvocation
from packages.tool_schema.models import ToolArguments, Unit


def _example(
    example_id: str,
    *,
    needs_tool: bool = True,
    language: str = "en",
    split: str = "test",
) -> BenchmarkExample:
    expected_tool_call = None
    unit_family = "none"
    if needs_tool:
        unit_family = "length"
        expected_tool_call = ToolInvocation(
            tool="units.convert",
            arguments=ToolArguments(
                value=2,
                from_unit=Unit.KILOMETER,
                to_unit=Unit.METER,
            ),
        )
    return BenchmarkExample(
        example_id=example_id,
        dataset_version="v1",
        language=language,  # type: ignore[arg-type]
        split=split,  # type: ignore[arg-type]
        unit_family=unit_family,  # type: ignore[arg-type]
        text="Convert 2 kilometers to meters.",
        needs_tool=needs_tool,
        expected_tool_call=expected_tool_call,
        expected_final_answer="2 kilometers is 2000 meters.",
        audio_id=f"{example_id}-audio",
    )


def _parsed_output(
    *,
    needs_tool: bool = True,
    value: float = 2,
    from_unit: str = "kilometer",
    to_unit: str = "meter",
) -> dict[str, Any]:
    tool_call = None
    if needs_tool:
        tool_call = {
            "tool": "units.convert",
            "arguments": {
                "value": value,
                "from_unit": from_unit,
                "to_unit": to_unit,
            },
        }
    return {
        "needs_tool": needs_tool,
        "tool_call": tool_call,
        "final_answer": "2 kilometers is 2000 meters.",
    }


def _record(
    example_id: str,
    *,
    parsed_output: dict[str, Any] | None,
    first_pass_parsable: bool = True,
    repair_attempted: bool = False,
    repair_success: bool = False,
    pipeline: str = "A",
) -> PipelineRunRecord:
    return PipelineRunRecord(
        run_id="run-001",
        pipeline=pipeline,  # type: ignore[arg-type]
        example_id=example_id,
        dataset_version="v1",
        model_adapter="MockModelAdapter",
        input_modality="text",
        raw_output="{}",
        parsed_output=parsed_output,
        first_pass_parsable=first_pass_parsable,
        repair_attempted=repair_attempted,
        repair_success=repair_success,
    )


def test_parsability_rate_counts_only_first_pass_parsable_records() -> None:
    examples = [_example("e1"), _example("e2"), _example("e3"), _example("e4")]
    records = [
        _record("e1", parsed_output=_parsed_output()),
        _record(
            "e2",
            parsed_output=_parsed_output(),
            first_pass_parsable=False,
            repair_attempted=True,
            repair_success=True,
        ),
        _record(
            "e3",
            parsed_output=None,
            first_pass_parsable=False,
            repair_attempted=True,
            repair_success=False,
        ),
        _record("e4", parsed_output=_parsed_output()),
    ]

    evaluations = evaluate_run(records, examples)

    # Repaired success must stay distinct from first-pass parsability.
    assert parsability_rate(evaluations) == pytest.approx(0.5)


def test_repair_success_rate_uses_only_repair_attempted_records() -> None:
    examples = [_example("e1"), _example("e2"), _example("e3")]
    records = [
        _record("e1", parsed_output=_parsed_output()),
        _record(
            "e2",
            parsed_output=_parsed_output(),
            first_pass_parsable=False,
            repair_attempted=True,
            repair_success=True,
        ),
        _record(
            "e3",
            parsed_output=None,
            first_pass_parsable=False,
            repair_attempted=True,
            repair_success=False,
        ),
    ]

    evaluations = evaluate_run(records, examples)

    assert repair_success_rate(evaluations) == pytest.approx(0.5)


def test_repair_success_rate_is_zero_when_no_repairs_attempted() -> None:
    examples = [_example("e1")]
    records = [_record("e1", parsed_output=_parsed_output())]

    evaluations = evaluate_run(records, examples)

    assert repair_success_rate(evaluations) == 0.0


def test_tool_decision_accuracy_compares_predicted_and_expected_labels() -> None:
    examples = [
        _example("e1", needs_tool=True),
        _example("e2", needs_tool=True),
        _example("e3", needs_tool=False),
        _example("e4", needs_tool=False),
    ]
    records = [
        _record("e1", parsed_output=_parsed_output(needs_tool=True)),
        _record("e2", parsed_output=_parsed_output(needs_tool=False)),
        _record("e3", parsed_output=_parsed_output(needs_tool=False)),
        _record("e4", parsed_output=_parsed_output(needs_tool=True)),
    ]

    evaluations = evaluate_run(records, examples)

    assert tool_decision_accuracy(evaluations) == pytest.approx(0.5)


def test_unparsable_record_counts_as_wrong_tool_decision() -> None:
    examples = [_example("e1", needs_tool=True)]
    records = [
        _record(
            "e1",
            parsed_output=None,
            first_pass_parsable=False,
            repair_attempted=True,
            repair_success=False,
        )
    ]

    evaluations = evaluate_run(records, examples)

    assert tool_decision_accuracy(evaluations) == 0.0


def test_confusion_matrix_counts_tool_and_no_tool_decisions() -> None:
    examples = [
        _example("e1", needs_tool=True),
        _example("e2", needs_tool=True),
        _example("e3", needs_tool=False),
        _example("e4", needs_tool=False),
        _example("e5", needs_tool=False),
    ]
    records = [
        _record("e1", parsed_output=_parsed_output(needs_tool=True)),
        _record("e2", parsed_output=_parsed_output(needs_tool=False)),
        _record("e3", parsed_output=_parsed_output(needs_tool=True)),
        _record("e4", parsed_output=_parsed_output(needs_tool=False)),
        _record("e5", parsed_output=_parsed_output(needs_tool=False)),
    ]

    matrix = confusion_matrix(evaluate_run(records, examples))

    assert matrix.true_positive == 1
    assert matrix.false_negative == 1
    assert matrix.false_positive == 1
    assert matrix.true_negative == 2


def test_precision_recall_and_false_alarm_rate_from_confusion_matrix() -> None:
    examples = [
        _example("e1", needs_tool=True),
        _example("e2", needs_tool=True),
        _example("e3", needs_tool=False),
        _example("e4", needs_tool=False),
        _example("e5", needs_tool=False),
        _example("e6", needs_tool=False),
    ]
    records = [
        _record("e1", parsed_output=_parsed_output(needs_tool=True)),
        _record("e2", parsed_output=_parsed_output(needs_tool=False)),
        _record("e3", parsed_output=_parsed_output(needs_tool=True)),
        _record("e4", parsed_output=_parsed_output(needs_tool=False)),
        _record("e5", parsed_output=_parsed_output(needs_tool=False)),
        _record("e6", parsed_output=_parsed_output(needs_tool=False)),
    ]

    matrix = confusion_matrix(evaluate_run(records, examples))

    assert precision(matrix) == pytest.approx(0.5)
    assert recall(matrix) == pytest.approx(0.5)
    assert false_alarm_rate(matrix) == pytest.approx(0.25)


def test_precision_recall_and_false_alarm_rate_handle_empty_denominators() -> None:
    examples = [_example("e1", needs_tool=False)]
    records = [_record("e1", parsed_output=_parsed_output(needs_tool=False))]

    matrix = confusion_matrix(evaluate_run(records, examples))

    assert precision(matrix) == 0.0
    assert recall(matrix) == 0.0
    assert false_alarm_rate(matrix) == 0.0
