from __future__ import annotations

from typing import Any

import pytest
from packages.dataset_builder.models import BenchmarkExample
from packages.metrics.tool_use import (
    argument_field_match_rates,
    evaluate_run,
    tool_call_exact_match_rate,
)
from packages.pipeline_runner.artifacts import PipelineRunRecord
from packages.tool_schema import ToolInvocation
from packages.tool_schema.models import ToolArguments, Unit


def _example(example_id: str, *, needs_tool: bool = True) -> BenchmarkExample:
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
        language="en",
        split="test",
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
    tool: str = "units.convert",
    value: float = 2,
    from_unit: str = "kilometer",
    to_unit: str = "meter",
) -> dict[str, Any]:
    tool_call = None
    if needs_tool:
        tool_call = {
            "tool": tool,
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
) -> PipelineRunRecord:
    return PipelineRunRecord(
        run_id="run-001",
        pipeline="A",
        example_id=example_id,
        dataset_version="v1",
        model_adapter="MockModelAdapter",
        input_modality="text",
        raw_output="{}",
        parsed_output=parsed_output,
        first_pass_parsable=first_pass_parsable,
        repair_attempted=not first_pass_parsable,
        repair_success=parsed_output is not None and not first_pass_parsable,
    )


def test_exact_match_requires_decision_name_value_and_both_units() -> None:
    examples = [
        _example("e1", needs_tool=True),
        _example("e2", needs_tool=True),
        _example("e3", needs_tool=True),
        _example("e4", needs_tool=False),
    ]
    records = [
        _record("e1", parsed_output=_parsed_output()),
        _record("e2", parsed_output=_parsed_output(value=3)),
        _record("e3", parsed_output=_parsed_output(to_unit="centimeter")),
        _record("e4", parsed_output=_parsed_output(needs_tool=False)),
    ]

    evaluations = evaluate_run(records, examples)

    # e1 and the correct no-tool decision e4 are exact; e2/e3 are partial.
    assert tool_call_exact_match_rate(evaluations) == pytest.approx(0.5)


def test_partially_correct_call_is_not_exact_but_counts_per_field() -> None:
    examples = [_example("e1", needs_tool=True), _example("e2", needs_tool=True)]
    records = [
        _record("e1", parsed_output=_parsed_output(value=999)),
        _record("e2", parsed_output=_parsed_output(from_unit="meter")),
    ]

    evaluations = evaluate_run(records, examples)
    rates = argument_field_match_rates(evaluations)

    assert tool_call_exact_match_rate(evaluations) == 0.0
    assert rates["argument_value_match"] == pytest.approx(0.5)
    assert rates["argument_from_unit_match"] == pytest.approx(0.5)
    assert rates["argument_to_unit_match"] == pytest.approx(1.0)


def test_missing_predicted_call_fails_every_argument_field() -> None:
    examples = [_example("e1", needs_tool=True), _example("e2", needs_tool=True)]
    records = [
        _record("e1", parsed_output=_parsed_output()),
        _record("e2", parsed_output=_parsed_output(needs_tool=False)),
    ]

    evaluations = evaluate_run(records, examples)
    rates = argument_field_match_rates(evaluations)

    assert rates["argument_value_match"] == pytest.approx(0.5)
    assert rates["argument_from_unit_match"] == pytest.approx(0.5)
    assert rates["argument_to_unit_match"] == pytest.approx(0.5)


def test_wrong_tool_name_blocks_exact_match() -> None:
    examples = [_example("e1", needs_tool=True)]
    records = [_record("e1", parsed_output=_parsed_output(tool="weather.lookup"))]

    evaluations = evaluate_run(records, examples)

    assert tool_call_exact_match_rate(evaluations) == 0.0
    assert evaluations[0].tool_name_match is False


def test_unparsable_record_is_not_exact_match() -> None:
    examples = [_example("e1", needs_tool=True)]
    records = [
        _record("e1", parsed_output=None, first_pass_parsable=False),
    ]

    evaluations = evaluate_run(records, examples)

    assert tool_call_exact_match_rate(evaluations) == 0.0


def test_argument_rates_are_zero_without_expected_tool_calls() -> None:
    examples = [_example("e1", needs_tool=False)]
    records = [_record("e1", parsed_output=_parsed_output(needs_tool=False))]

    rates = argument_field_match_rates(evaluate_run(records, examples))

    assert rates["argument_value_match"] == 0.0
    assert rates["argument_from_unit_match"] == 0.0
    assert rates["argument_to_unit_match"] == 0.0
