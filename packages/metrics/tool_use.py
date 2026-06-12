from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from packages.dataset_builder.models import BenchmarkExample
from packages.pipeline_runner.artifacts import PipelineRunRecord

_VALUE_TOLERANCE = 1e-9


class ToolUseEvaluation(BaseModel):
    """Per-example tool-use scoring derived from one pipeline run record."""

    model_config = ConfigDict(extra="forbid")

    example_id: str
    pipeline: Literal["A", "B", "C", "D"]
    language: Literal["en", "ru"]
    split: Literal["train", "validation", "test"]
    first_pass_parsable: bool
    repair_attempted: bool
    repair_success: bool
    expected_needs_tool: bool
    predicted_needs_tool: bool | None
    tool_name_match: bool | None
    value_match: bool | None
    from_unit_match: bool | None
    to_unit_match: bool | None
    exact_match: bool
    wer: float | None = None


class ConfusionMatrix(BaseModel):
    """Tool/no-tool decision confusion counts for a set of evaluations."""

    model_config = ConfigDict(extra="forbid")

    true_positive: int
    false_positive: int
    false_negative: int
    true_negative: int


def _predicted_tool_call(parsed_output: dict[str, Any] | None) -> dict[str, Any] | None:
    """Extract the predicted tool call mapping from a parsed envelope."""
    if not isinstance(parsed_output, dict):
        return None
    tool_call = parsed_output.get("tool_call")
    return tool_call if isinstance(tool_call, dict) else None


def _values_equal(expected: float, observed: Any) -> bool:
    """Compare a numeric argument with tolerance for float round-trips."""
    if not isinstance(observed, (int, float)) or isinstance(observed, bool):
        return False
    return math.isclose(float(expected), float(observed), abs_tol=_VALUE_TOLERANCE)


def evaluate_example(
    record: PipelineRunRecord,
    example: BenchmarkExample,
) -> ToolUseEvaluation:
    """Score one pipeline run record against its benchmark expectation."""
    parsed = record.parsed_output
    predicted_needs_tool = (
        bool(parsed["needs_tool"])
        if isinstance(parsed, dict) and isinstance(parsed.get("needs_tool"), bool)
        else None
    )
    predicted_call = _predicted_tool_call(parsed)

    tool_name_match: bool | None = None
    value_match: bool | None = None
    from_unit_match: bool | None = None
    to_unit_match: bool | None = None
    if example.expected_tool_call is not None:
        expected = example.expected_tool_call
        if predicted_call is None:
            tool_name_match = value_match = from_unit_match = to_unit_match = False
        else:
            arguments = predicted_call.get("arguments")
            arguments = arguments if isinstance(arguments, dict) else {}
            tool_name_match = predicted_call.get("tool") == expected.tool
            value_match = _values_equal(
                expected.arguments.value, arguments.get("value")
            )
            from_unit_match = (
                arguments.get("from_unit") == expected.arguments.from_unit.value
            )
            to_unit_match = arguments.get("to_unit") == expected.arguments.to_unit.value

    decision_correct = predicted_needs_tool == example.needs_tool
    if example.needs_tool:
        exact_match = decision_correct and all(
            field is True
            for field in (tool_name_match, value_match, from_unit_match, to_unit_match)
        )
    else:
        exact_match = decision_correct

    return ToolUseEvaluation(
        example_id=record.example_id,
        pipeline=record.pipeline,
        language=example.language,
        split=example.split,
        first_pass_parsable=record.first_pass_parsable,
        repair_attempted=record.repair_attempted,
        repair_success=record.repair_success,
        expected_needs_tool=example.needs_tool,
        predicted_needs_tool=predicted_needs_tool,
        tool_name_match=tool_name_match,
        value_match=value_match,
        from_unit_match=from_unit_match,
        to_unit_match=to_unit_match,
        exact_match=exact_match,
        wer=record.wer,
    )


def evaluate_run(
    records: Sequence[PipelineRunRecord],
    examples: Sequence[BenchmarkExample],
) -> list[ToolUseEvaluation]:
    """Join pipeline records with benchmark examples and score each pair."""
    examples_by_id = {example.example_id: example for example in examples}
    evaluations: list[ToolUseEvaluation] = []
    for record in records:
        example = examples_by_id.get(record.example_id)
        if example is None:
            raise ValueError(f"No benchmark example for record {record.example_id!r}")
        evaluations.append(evaluate_example(record, example))
    return evaluations


def _rate(numerator: int, denominator: int) -> float:
    """Return a safe ratio that treats an empty denominator as zero."""
    return numerator / denominator if denominator else 0.0


def parsability_rate(evaluations: Iterable[ToolUseEvaluation]) -> float:
    """Fraction of records whose first-pass output was a valid envelope."""
    items = list(evaluations)
    return _rate(sum(item.first_pass_parsable for item in items), len(items))


def repair_success_rate(evaluations: Iterable[ToolUseEvaluation]) -> float:
    """Fraction of attempted repairs that produced a valid envelope."""
    attempted = [item for item in evaluations if item.repair_attempted]
    return _rate(sum(item.repair_success for item in attempted), len(attempted))


def tool_decision_accuracy(evaluations: Iterable[ToolUseEvaluation]) -> float:
    """Fraction of records whose tool/no-tool decision matches the label."""
    items = list(evaluations)
    correct = sum(
        item.predicted_needs_tool == item.expected_needs_tool for item in items
    )
    return _rate(correct, len(items))


def confusion_matrix(evaluations: Iterable[ToolUseEvaluation]) -> ConfusionMatrix:
    """Count tool/no-tool decision outcomes; unparsable predicts no decision."""
    true_positive = false_positive = false_negative = true_negative = 0
    for item in evaluations:
        if item.expected_needs_tool:
            if item.predicted_needs_tool is True:
                true_positive += 1
            else:
                false_negative += 1
        elif item.predicted_needs_tool is True:
            false_positive += 1
        else:
            true_negative += 1
    return ConfusionMatrix(
        true_positive=true_positive,
        false_positive=false_positive,
        false_negative=false_negative,
        true_negative=true_negative,
    )


def precision(matrix: ConfusionMatrix) -> float:
    """Fraction of predicted tool calls that were actually required."""
    return _rate(matrix.true_positive, matrix.true_positive + matrix.false_positive)


def recall(matrix: ConfusionMatrix) -> float:
    """Fraction of required tool calls that were predicted."""
    return _rate(matrix.true_positive, matrix.true_positive + matrix.false_negative)


def false_alarm_rate(matrix: ConfusionMatrix) -> float:
    """Fraction of no-tool examples that wrongly triggered a tool call."""
    return _rate(matrix.false_positive, matrix.false_positive + matrix.true_negative)


def tool_call_exact_match_rate(evaluations: Iterable[ToolUseEvaluation]) -> float:
    """Fraction of records with a fully correct decision, name, and arguments."""
    items = list(evaluations)
    return _rate(sum(item.exact_match for item in items), len(items))


def argument_field_match_rates(
    evaluations: Iterable[ToolUseEvaluation],
) -> dict[str, float]:
    """Per-field argument diagnostics over examples expecting a tool call."""
    expected = [item for item in evaluations if item.expected_needs_tool]
    total = len(expected)
    return {
        "argument_value_match": _rate(
            sum(item.value_match is True for item in expected), total
        ),
        "argument_from_unit_match": _rate(
            sum(item.from_unit_match is True for item in expected), total
        ),
        "argument_to_unit_match": _rate(
            sum(item.to_unit_match is True for item in expected), total
        ),
    }
