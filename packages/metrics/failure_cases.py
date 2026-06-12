from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

from pydantic import BaseModel, ConfigDict

from packages.dataset_builder.models import BenchmarkExample
from packages.metrics.tool_use import ToolUseEvaluation, evaluate_example
from packages.pipeline_runner.artifacts import PipelineRunRecord

FailureCategory = Literal[
    "json_parsing",
    "repair_failed",
    "schema_validation",
    "unknown_tool",
    "duplicate_tool_provider",
    "invalid_arguments",
    "tool_decision",
    "tool_name",
    "numeric_value",
    "source_unit",
    "target_unit",
    "transcript",
    "execution",
    "answer",
]

_STRUCTURED_FAILURE_CATEGORIES: dict[str, FailureCategory] = {
    "unknown_tool": "unknown_tool",
    "duplicate_tool_provider": "duplicate_tool_provider",
    "invalid_arguments": "invalid_arguments",
    "execution_error": "execution",
}


class FailureCase(BaseModel):
    """One categorized benchmark failure for the report's failure analysis."""

    model_config = ConfigDict(extra="forbid")

    run_id: str
    pipeline: Literal["A", "B", "C", "D"]
    example_id: str
    language: Literal["en", "ru"]
    failure_category: FailureCategory
    expected_summary: str
    observed_summary: str
    raw_output_path: str | None = None


def _expected_summary(example: BenchmarkExample) -> str:
    """Describe the expected tool behavior for a benchmark example."""
    if example.expected_tool_call is None:
        return f"no tool; answer: {example.expected_final_answer}"
    arguments = example.expected_tool_call.arguments
    return (
        f"{example.expected_tool_call.tool}"
        f"(value={arguments.value}, from={arguments.from_unit.value}, "
        f"to={arguments.to_unit.value})"
    )


def _categorize(
    record: PipelineRunRecord,
    evaluation: ToolUseEvaluation,
) -> tuple[FailureCategory, str] | None:
    """Pick the highest-priority failure category, or None when correct."""
    if record.parsed_output is None:
        if record.repair_attempted and not record.repair_success:
            return "repair_failed", "repair attempt did not recover valid JSON"
        return "json_parsing", "model output was not parsable JSON"
    if record.validation_errors:
        return "schema_validation", "; ".join(record.validation_errors)
    for failure in record.structured_failures:
        category = _STRUCTURED_FAILURE_CATEGORIES.get(failure.failure_type)
        if category is not None:
            return category, failure.message
    if evaluation.predicted_needs_tool != evaluation.expected_needs_tool:
        return (
            "tool_decision",
            f"predicted needs_tool={evaluation.predicted_needs_tool}",
        )
    if evaluation.expected_needs_tool:
        if evaluation.tool_name_match is False:
            return "tool_name", "predicted tool name differs from expectation"
        if evaluation.value_match is False:
            return "numeric_value", "predicted value differs from expectation"
        if evaluation.from_unit_match is False:
            return "source_unit", "predicted from_unit differs from expectation"
        if evaluation.to_unit_match is False:
            return "target_unit", "predicted to_unit differs from expectation"
    return None


def categorize_failures(
    records: Sequence[PipelineRunRecord],
    examples: Sequence[BenchmarkExample],
) -> list[FailureCase]:
    """Categorize each failed record into the contract failure taxonomy."""
    examples_by_id = {example.example_id: example for example in examples}
    cases: list[FailureCase] = []
    for record in records:
        example = examples_by_id.get(record.example_id)
        if example is None:
            raise ValueError(f"No benchmark example for record {record.example_id!r}")
        evaluation = evaluate_example(record, example)
        categorized = _categorize(record, evaluation)
        if categorized is None:
            continue
        category, observed = categorized
        cases.append(
            FailureCase(
                run_id=record.run_id,
                pipeline=record.pipeline,
                example_id=record.example_id,
                language=example.language,
                failure_category=category,
                expected_summary=_expected_summary(example),
                observed_summary=observed,
            )
        )
    return cases
