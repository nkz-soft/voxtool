from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    """Parse script arguments and build the benchmark markdown report."""
    from packages.dataset_builder.io import read_jsonl
    from packages.metrics.aggregation import summarize_metrics, write_summary
    from packages.pipeline_runner.artifacts import (
        PipelineRunRecord,
        read_pipeline_jsonl,
    )
    from packages.report_builder.report import build_report, write_report

    parser = argparse.ArgumentParser(description="Build a markdown benchmark report.")
    parser.add_argument("--dataset", required=True)
    parser.add_argument(
        "--run",
        action="append",
        required=True,
        help="Pipeline output JSONL (repeatable).",
    )
    parser.add_argument("--output", required=True)
    parser.add_argument("--summary", default=None)
    parser.add_argument("--plots-dir", default=None)
    args = parser.parse_args()

    examples = read_jsonl(Path(args.dataset))
    records_by_pipeline: dict[str, list[PipelineRunRecord]] = {}
    for run_path in args.run:
        records = read_pipeline_jsonl(Path(run_path))
        if not records:
            parser.error(f"Run file has no records: {run_path}")
        pipelines = {record.pipeline for record in records}
        if len(pipelines) != 1:
            parser.error(f"Run file mixes pipelines {sorted(pipelines)}: {run_path}")
        records_by_pipeline.setdefault(pipelines.pop(), []).extend(records)

    metrics_summary = summarize_metrics(
        dataset=examples, records_by_pipeline=records_by_pipeline
    )

    plot_paths: list[Path] = []
    if args.plots_dir is not None:
        from packages.report_builder.plots import save_report_plots

        plot_paths = save_report_plots(
            dataset=examples,
            records_by_pipeline=records_by_pipeline,
            summary=metrics_summary,
            plots_dir=Path(args.plots_dir),
        )

    report = build_report(
        dataset=examples,
        records_by_pipeline=records_by_pipeline,
        plot_paths=plot_paths,
    )
    write_report(Path(args.output), report)
    if args.summary is not None:
        write_summary(metrics_summary, Path(args.summary))


if __name__ == "__main__":
    main()
