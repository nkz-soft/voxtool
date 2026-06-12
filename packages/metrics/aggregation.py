from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import pandas as pd

from packages.dataset_builder.models import BenchmarkExample
from packages.metrics.modality_gap import modality_gap
from packages.metrics.tool_use import (
    ToolUseEvaluation,
    argument_field_match_rates,
    confusion_matrix,
    evaluate_run,
    false_alarm_rate,
    parsability_rate,
    precision,
    recall,
    repair_success_rate,
    tool_call_exact_match_rate,
    tool_decision_accuracy,
)
from packages.pipeline_runner.artifacts import PipelineRunRecord

SUMMARY_COLUMNS = [
    "run_id",
    "pipeline",
    "split",
    "language",
    "parsable_tool_invocation_rate",
    "repair_success_rate",
    "tool_decision_accuracy",
    "tool_call_exact_match",
    "argument_value_match",
    "argument_from_unit_match",
    "argument_to_unit_match",
    "precision",
    "recall",
    "false_alarm_rate",
    "wer",
    "modality_gap",
]

TEXT_BASELINE_PIPELINE = "A"


def _subset(
    evaluations: Sequence[ToolUseEvaluation],
    split: str,
    language: str,
) -> list[ToolUseEvaluation]:
    """Filter evaluations by split and language, where "all" keeps everything."""
    return [
        item
        for item in evaluations
        if (split == "all" or item.split == split)
        and (language == "all" or item.language == language)
    ]


def _mean_wer(evaluations: Sequence[ToolUseEvaluation]) -> float | None:
    """Average per-example WER, or None when no record carries a transcript."""
    values = [item.wer for item in evaluations if item.wer is not None]
    return sum(values) / len(values) if values else None


def _summary_row(
    *,
    run_id: str,
    pipeline: str,
    split: str,
    language: str,
    evaluations: Sequence[ToolUseEvaluation],
    baseline: Sequence[ToolUseEvaluation] | None,
) -> dict[str, Any]:
    """Build one metrics summary row for a (pipeline, split, language) subset."""
    matrix = confusion_matrix(evaluations)
    argument_rates = argument_field_match_rates(evaluations)
    gap = None
    if baseline is not None:
        gap = modality_gap(list(baseline), list(evaluations))
    return {
        "run_id": run_id,
        "pipeline": pipeline,
        "split": split,
        "language": language,
        "parsable_tool_invocation_rate": parsability_rate(evaluations),
        "repair_success_rate": repair_success_rate(evaluations),
        "tool_decision_accuracy": tool_decision_accuracy(evaluations),
        "tool_call_exact_match": tool_call_exact_match_rate(evaluations),
        **argument_rates,
        "precision": precision(matrix),
        "recall": recall(matrix),
        "false_alarm_rate": false_alarm_rate(matrix),
        "wer": _mean_wer(evaluations),
        "modality_gap": gap,
    }


def summarize_metrics(
    *,
    dataset: Sequence[BenchmarkExample],
    records_by_pipeline: Mapping[str, Sequence[PipelineRunRecord]],
) -> pd.DataFrame:
    """Aggregate per-pipeline metrics into a contract-shaped DataFrame.

    Rows cover overall, per-split, and per-language subsets for each pipeline.
    Audio pipelines report a modality gap against the Pipeline A text baseline
    when paired example IDs exist.
    """
    evaluations_by_pipeline = {
        pipeline: evaluate_run(list(records), dataset)
        for pipeline, records in records_by_pipeline.items()
    }
    baseline = evaluations_by_pipeline.get(TEXT_BASELINE_PIPELINE)

    rows: list[dict[str, Any]] = []
    for pipeline in sorted(evaluations_by_pipeline):
        evaluations = evaluations_by_pipeline[pipeline]
        records = list(records_by_pipeline[pipeline])
        run_id = records[0].run_id if records else "unknown"
        splits = ["all", *sorted({item.split for item in evaluations})]
        languages = ["all", *sorted({item.language for item in evaluations})]
        pipeline_baseline = (
            baseline if pipeline != TEXT_BASELINE_PIPELINE and baseline else None
        )
        for split in splits:
            for language in languages:
                subset = _subset(evaluations, split, language)
                if not subset:
                    continue
                baseline_subset = (
                    _subset(pipeline_baseline, split, language)
                    if pipeline_baseline is not None
                    else None
                )
                rows.append(
                    _summary_row(
                        run_id=run_id,
                        pipeline=pipeline,
                        split=split,
                        language=language,
                        evaluations=subset,
                        baseline=baseline_subset,
                    )
                )
    return pd.DataFrame(rows, columns=SUMMARY_COLUMNS)


def write_summary(summary: pd.DataFrame, path: Path) -> None:
    """Write a metrics summary as CSV or Parquet based on the path suffix."""
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        summary.to_csv(path, index=False)
    elif suffix == ".parquet":
        summary.to_parquet(path, index=False)
    else:
        raise ValueError(f"Unsupported summary format: {path.suffix!r}")
