from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path

import pandas as pd
from pydantic import BaseModel, ConfigDict

from packages.dataset_builder.models import BenchmarkExample
from packages.metrics.aggregation import summarize_metrics
from packages.metrics.failure_cases import FailureCase, categorize_failures
from packages.metrics.tool_use import ConfusionMatrix, confusion_matrix, evaluate_run
from packages.pipeline_runner.artifacts import PipelineRunRecord


class BestPipeline(BaseModel):
    """Selected best pipeline with a human-readable selection rationale."""

    model_config = ConfigDict(extra="forbid")

    pipeline: str
    rationale: str


def _format_number(value: object) -> str:
    """Render a metric cell, leaving missing optional metrics blank."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "-"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def _markdown_table(frame: pd.DataFrame) -> str:
    """Render a DataFrame as a GitHub-flavored markdown table."""
    if frame.empty:
        return "_No data._"
    header = "| " + " | ".join(str(column) for column in frame.columns) + " |"
    divider = "| " + " | ".join("---" for _ in frame.columns) + " |"
    rows = [
        "| " + " | ".join(_format_number(value) for value in row) + " |"
        for row in frame.itertuples(index=False)
    ]
    return "\n".join([header, divider, *rows])


def _dataset_summary_section(dataset: Sequence[BenchmarkExample]) -> str:
    """Summarize dataset size and language/split/tool balance."""
    language_counts = Counter(example.language for example in dataset)
    split_counts = Counter(example.split for example in dataset)
    needs_tool = sum(example.needs_tool for example in dataset)
    lines = [
        f"- Total examples: {len(dataset)}",
        f"- Tool examples: {needs_tool}",
        f"- No-tool examples: {len(dataset) - needs_tool}",
    ]
    lines.extend(
        f"- Language `{language}`: {count}"
        for language, count in sorted(language_counts.items())
    )
    lines.extend(
        f"- Split `{split}`: {count}" for split, count in sorted(split_counts.items())
    )
    return "\n".join(lines)


def _confusion_section(
    dataset: Sequence[BenchmarkExample],
    records_by_pipeline: Mapping[str, Sequence[PipelineRunRecord]],
) -> str:
    """Render per-pipeline tool/no-tool confusion matrices."""
    matrices: dict[str, ConfusionMatrix] = {
        pipeline: confusion_matrix(evaluate_run(list(records), dataset))
        for pipeline, records in sorted(records_by_pipeline.items())
    }
    frame = pd.DataFrame(
        [
            {
                "pipeline": pipeline,
                "true_positive": matrix.true_positive,
                "false_positive": matrix.false_positive,
                "false_negative": matrix.false_negative,
                "true_negative": matrix.true_negative,
            }
            for pipeline, matrix in matrices.items()
        ]
    )
    return _markdown_table(frame)


def _failure_section(cases: Sequence[FailureCase]) -> str:
    """Render categorized failure cases as a markdown table."""
    if not cases:
        return "_No failures recorded._"
    frame = pd.DataFrame(
        [
            {
                "pipeline": case.pipeline,
                "example_id": case.example_id,
                "language": case.language,
                "failure_category": case.failure_category,
                "expected": case.expected_summary,
                "observed": case.observed_summary,
            }
            for case in cases
        ]
    )
    return _markdown_table(frame)


def select_best_pipeline(
    *,
    dataset: Sequence[BenchmarkExample],
    records_by_pipeline: Mapping[str, Sequence[PipelineRunRecord]],
) -> BestPipeline:
    """Pick the pipeline with the best overall exact-match performance.

    Exact match is the primary criterion; tool decision accuracy and
    first-pass parsability break ties.
    """
    summary = summarize_metrics(
        dataset=dataset, records_by_pipeline=records_by_pipeline
    )
    overall = summary[(summary["split"] == "all") & (summary["language"] == "all")]
    if overall.empty:
        raise ValueError("No pipeline metrics available for best-pipeline selection")
    ranked = overall.sort_values(
        by=[
            "tool_call_exact_match",
            "tool_decision_accuracy",
            "parsable_tool_invocation_rate",
            "pipeline",
        ],
        ascending=[False, False, False, True],
    )
    best = ranked.iloc[0]
    rationale = (
        f"Pipeline {best['pipeline']} has the highest tool-call exact match "
        f"({best['tool_call_exact_match']:.3f}) with tool decision accuracy "
        f"{best['tool_decision_accuracy']:.3f} and first-pass parsability "
        f"{best['parsable_tool_invocation_rate']:.3f}."
    )
    return BestPipeline(pipeline=str(best["pipeline"]), rationale=rationale)


def build_report(
    *,
    dataset: Sequence[BenchmarkExample],
    records_by_pipeline: Mapping[str, Sequence[PipelineRunRecord]],
    plot_paths: Sequence[Path] = (),
) -> str:
    """Build the final markdown benchmark report from run artifacts."""
    summary = summarize_metrics(
        dataset=dataset, records_by_pipeline=records_by_pipeline
    )
    overall = summary[(summary["split"] == "all") & (summary["language"] == "all")]
    by_language = summary[(summary["split"] == "all") & (summary["language"] != "all")]
    wer_frame = overall[["pipeline", "wer"]]
    gap_frame = overall[["pipeline", "modality_gap"]]
    failure_cases: list[FailureCase] = []
    for _, records in sorted(records_by_pipeline.items()):
        failure_cases.extend(categorize_failures(list(records), dataset))
    best = select_best_pipeline(
        dataset=dataset, records_by_pipeline=records_by_pipeline
    )

    sections = [
        "# VoxTool Benchmark Report",
        "## Dataset Summary",
        _dataset_summary_section(dataset),
        "## Per-Pipeline Metrics",
        _markdown_table(overall),
        "## Language Splits",
        _markdown_table(by_language),
        "## Confusion Matrix",
        _confusion_section(dataset, records_by_pipeline),
        "## ASR WER",
        _markdown_table(wer_frame),
        "## Modality Gap",
        _markdown_table(gap_frame),
        "## Best Pipeline",
        f"**Pipeline {best.pipeline}.** {best.rationale}",
        "## Failure Cases",
        _failure_section(failure_cases),
    ]
    if plot_paths:
        sections.append("## Plots")
        sections.extend(f"![{path.stem}]({path.as_posix()})" for path in plot_paths)
    return "\n\n".join(sections) + "\n"


def write_report(path: Path, content: str) -> None:
    """Write the markdown report, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
