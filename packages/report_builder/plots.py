from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from packages.dataset_builder.models import BenchmarkExample
from packages.metrics.tool_use import confusion_matrix, evaluate_run
from packages.pipeline_runner.artifacts import PipelineRunRecord


def plot_exact_match_by_pipeline(summary: pd.DataFrame, path: Path) -> Path:
    """Save a bar chart of overall tool-call exact match per pipeline."""
    overall = summary[(summary["split"] == "all") & (summary["language"] == "all")]
    figure, axis = plt.subplots(figsize=(6, 4))
    axis.bar(overall["pipeline"], overall["tool_call_exact_match"])
    axis.set_xlabel("Pipeline")
    axis.set_ylabel("Tool-call exact match")
    axis.set_ylim(0, 1)
    axis.set_title("Tool-call exact match by pipeline")
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, bbox_inches="tight")
    plt.close(figure)
    return path


def plot_confusion_matrices(
    dataset: Sequence[BenchmarkExample],
    records_by_pipeline: Mapping[str, Sequence[PipelineRunRecord]],
    path: Path,
) -> Path:
    """Save per-pipeline tool/no-tool confusion matrices as heatmaps."""
    pipelines = sorted(records_by_pipeline)
    figure, axes = plt.subplots(
        1, len(pipelines), figsize=(4 * len(pipelines), 4), squeeze=False
    )
    for axis, pipeline in zip(axes[0], pipelines, strict=True):
        matrix = confusion_matrix(
            evaluate_run(list(records_by_pipeline[pipeline]), dataset)
        )
        cells = [
            [matrix.true_positive, matrix.false_negative],
            [matrix.false_positive, matrix.true_negative],
        ]
        axis.imshow(cells, cmap="Blues")
        for row in range(2):
            for column in range(2):
                axis.text(column, row, str(cells[row][column]), ha="center")
        axis.set_xticks([0, 1], ["pred tool", "pred no-tool"])
        axis.set_yticks([0, 1], ["needs tool", "no tool"])
        axis.set_title(f"Pipeline {pipeline}")
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, bbox_inches="tight")
    plt.close(figure)
    return path


def save_report_plots(
    *,
    dataset: Sequence[BenchmarkExample],
    records_by_pipeline: Mapping[str, Sequence[PipelineRunRecord]],
    summary: pd.DataFrame,
    plots_dir: Path,
) -> list[Path]:
    """Save the standard report plot set and return the written paths."""
    return [
        plot_exact_match_by_pipeline(summary, plots_dir / "exact_match.png"),
        plot_confusion_matrices(
            dataset, records_by_pipeline, plots_dir / "confusion_matrix.png"
        ),
    ]
