from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AdvancedMetricResult(BaseModel):
    """One advanced metric row covering per-tool, Russian-only, and comparison runs.

    Defaults to the ``"all"`` subset so a plain result describes the whole
    evaluated set. ``tool``/``category`` narrow the subset, ``russian_only``
    flags Russian adaptation rows, and ``base_value``/``candidate_value``/
    ``delta`` carry paired base-vs-candidate comparisons.
    """

    model_config = ConfigDict(extra="forbid")

    run_id: str = Field(min_length=1)
    pipeline: str = Field(min_length=1)
    split: str = "all"
    language: str = "all"
    tool: str = "all"
    category: str = "all"
    parsable_rate: float | None = None
    repair_success_rate: float | None = None
    tool_decision_accuracy: float | None = None
    tool_call_exact_match: float | None = None
    argument_exact_match: float | None = None
    false_alarm_rate: float | None = None
    execution_success_rate: float | None = None
    latency_ms_per_example: float | None = None
    memory_note: str | None = None
    russian_only: bool = False
    base_value: float | None = None
    candidate_value: float | None = None
    delta: float | None = None


def compute_delta(
    base_value: float | None, candidate_value: float | None
) -> float | None:
    """Return ``candidate_value - base_value``, or None if either is missing."""
    if base_value is None or candidate_value is None:
        return None
    return candidate_value - base_value


def comparison_result(
    *,
    run_id: str,
    pipeline: str,
    base_value: float | None,
    candidate_value: float | None,
    **fields: Any,
) -> AdvancedMetricResult:
    """Build a paired base-vs-candidate result with the delta filled in.

    Used for base-vs-LoRA and base-vs-quantized comparisons, which must compare
    the same examples for both values.
    """
    return AdvancedMetricResult(
        run_id=run_id,
        pipeline=pipeline,
        base_value=base_value,
        candidate_value=candidate_value,
        delta=compute_delta(base_value, candidate_value),
        **fields,
    )


def russian_only_result(
    *,
    run_id: str,
    pipeline: str,
    **fields: Any,
) -> AdvancedMetricResult:
    """Build a result flagged as Russian-only, defaulting ``language`` to ``ru``."""
    fields.setdefault("language", "ru")
    return AdvancedMetricResult(
        run_id=run_id,
        pipeline=pipeline,
        russian_only=True,
        **fields,
    )


def per_tool_result(
    *,
    run_id: str,
    pipeline: str,
    tool: str,
    **fields: Any,
) -> AdvancedMetricResult:
    """Build a result grouped to a single tool such as ``units.convert``."""
    return AdvancedMetricResult(
        run_id=run_id,
        pipeline=pipeline,
        tool=tool,
        **fields,
    )
