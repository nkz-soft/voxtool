from packages.metrics.advanced import (
    AdvancedMetricResult,
    comparison_result,
    compute_delta,
    per_tool_result,
    russian_only_result,
)


def test_advanced_metric_result_has_aggregation_defaults() -> None:
    result = AdvancedMetricResult(run_id="run-1", pipeline="A")

    assert result.split == "all"
    assert result.language == "all"
    assert result.tool == "all"
    assert result.category == "all"
    assert result.russian_only is False
    assert result.base_value is None
    assert result.candidate_value is None
    assert result.delta is None
    assert result.latency_ms_per_example is None
    assert result.memory_note is None


def test_compute_delta_subtracts_base_from_candidate() -> None:
    assert compute_delta(0.80, 0.90) == 0.90 - 0.80
    assert compute_delta(None, 0.9) is None
    assert compute_delta(0.9, None) is None


def test_comparison_result_records_paired_values_and_delta() -> None:
    result = comparison_result(
        run_id="run-1",
        pipeline="A",
        base_value=0.80,
        candidate_value=0.90,
        memory_note="4bit uses less memory than base precision.",
    )

    assert result.base_value == 0.80
    assert result.candidate_value == 0.90
    assert result.delta == 0.90 - 0.80
    assert result.memory_note == "4bit uses less memory than base precision."


def test_russian_only_result_marks_language_and_flag() -> None:
    result = russian_only_result(
        run_id="run-1",
        pipeline="A",
        tool_decision_accuracy=0.95,
    )

    assert result.russian_only is True
    assert result.language == "ru"
    assert result.tool_decision_accuracy == 0.95


def test_per_tool_result_groups_by_tool_with_latency() -> None:
    result = per_tool_result(
        run_id="run-1",
        pipeline="A",
        tool="units.convert",
        tool_call_exact_match=1.0,
        latency_ms_per_example=42.0,
    )

    assert result.tool == "units.convert"
    assert result.tool_call_exact_match == 1.0
    assert result.latency_ms_per_example == 42.0
