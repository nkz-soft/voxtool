from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from packages.dataset_builder.io import read_jsonl
from packages.metrics.aggregation import summarize_metrics, write_summary
from packages.pipeline_runner.artifacts import (
    PipelineRunRecord,
    read_pipeline_jsonl,
)
from packages.report_builder.report import build_report, write_report

app = typer.Typer(help="Benchmark report commands.")


def _load_runs(run_paths: list[Path]) -> dict[str, list[PipelineRunRecord]]:
    """Load pipeline run JSONL files keyed by the pipeline they contain."""
    records_by_pipeline: dict[str, list[PipelineRunRecord]] = {}
    for run_path in run_paths:
        records = read_pipeline_jsonl(run_path)
        if not records:
            raise typer.BadParameter(f"Run file has no records: {run_path}")
        pipelines = {record.pipeline for record in records}
        if len(pipelines) != 1:
            raise typer.BadParameter(
                f"Run file mixes pipelines {sorted(pipelines)}: {run_path}"
            )
        records_by_pipeline.setdefault(pipelines.pop(), []).extend(records)
    return records_by_pipeline


@app.command()
def build(
    dataset: Annotated[
        Path, typer.Option("--dataset", help="Benchmark dataset JSONL.")
    ],
    run: Annotated[
        list[Path],
        typer.Option("--run", help="Pipeline output JSONL (repeatable)."),
    ],
    output: Annotated[
        Path, typer.Option("--output", help="Markdown report output path.")
    ],
    summary: Annotated[
        Path | None,
        typer.Option("--summary", help="Metrics summary CSV or Parquet path."),
    ] = None,
    plots_dir: Annotated[
        Path | None,
        typer.Option("--plots-dir", help="Directory for report plot images."),
    ] = None,
) -> None:
    """Aggregate run artifacts into a markdown report with summaries and plots."""
    examples = read_jsonl(dataset)
    records_by_pipeline = _load_runs(run)
    metrics_summary = summarize_metrics(
        dataset=examples, records_by_pipeline=records_by_pipeline
    )

    plot_paths: list[Path] = []
    if plots_dir is not None:
        from packages.report_builder.plots import save_report_plots

        plot_paths = save_report_plots(
            dataset=examples,
            records_by_pipeline=records_by_pipeline,
            summary=metrics_summary,
            plots_dir=plots_dir,
        )

    report = build_report(
        dataset=examples,
        records_by_pipeline=records_by_pipeline,
        plot_paths=plot_paths,
    )
    write_report(output, report)
    if summary is not None:
        write_summary(metrics_summary, summary)

    typer.echo(f"wrote report for pipelines {sorted(records_by_pipeline)} to {output}")
