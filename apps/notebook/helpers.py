"""Helper functions for the final voice benchmark demonstration notebook.

The helpers wrap existing package APIs so the notebook stays thin: loading
dataset and audio artifacts, running deterministic mock benchmark pipelines,
selecting bilingual display examples, and flattening run records into pandas
DataFrames for review.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import pandas as pd
from packages.dataset_builder.io import read_jsonl as read_dataset_jsonl
from packages.dataset_builder.models import BenchmarkExample
from packages.metrics.aggregation import summarize_metrics
from packages.pipeline_runner.artifacts import (
    PipelineRunRecord,
    read_pipeline_jsonl,
)
from packages.pipeline_runner.runner import run_benchmark
from packages.tool_schema.providers import ToolExecutor
from packages.tool_schema.units import default_tool_registry
from packages.tts_synth import SynthesisSettings, synthesize_dataset
from packages.tts_synth.io import write_jsonl as write_audio_jsonl
from packages.tts_synth.models import AudioExample

PipelineName = Literal["A", "B", "C", "D"]


def load_examples(path: Path) -> list[BenchmarkExample]:
    """Load benchmark dataset examples from a JSONL file."""
    return read_dataset_jsonl(path)


def select_bilingual_examples(
    examples: list[BenchmarkExample],
) -> list[BenchmarkExample]:
    """Pick one tool and one no-tool example per language when available.

    Returns at most four examples ordered by language then tool usage so the
    notebook can display a compact Russian/English comparison.
    """
    selected: list[BenchmarkExample] = []
    for language in ("ru", "en"):
        for needs_tool in (True, False):
            match = next(
                (
                    example
                    for example in examples
                    if example.language == language and example.needs_tool == needs_tool
                ),
                None,
            )
            if match is not None:
                selected.append(match)
    return selected


def examples_table(examples: list[BenchmarkExample]) -> pd.DataFrame:
    """Flatten dataset examples into a DataFrame for notebook display."""
    return pd.DataFrame(
        [
            {
                "example_id": example.example_id,
                "language": example.language,
                "split": example.split,
                "needs_tool": example.needs_tool,
                "text": example.text,
                "expected_final_answer": example.expected_final_answer,
            }
            for example in examples
        ]
    )


def synthesize_audio_metadata(
    examples: list[BenchmarkExample],
    output_dir: Path,
) -> tuple[Path, list[AudioExample]]:
    """Synthesize deterministic audio fixtures and write metadata JSONL.

    Returns the metadata path and records. Uses the local fixture engine, so
    no cloud service or model download is required.
    """
    settings = SynthesisSettings(engine="fixture-silent")
    records = synthesize_dataset(examples, output_dir=output_dir, settings=settings)
    metadata_path = output_dir / "audio.jsonl"
    write_audio_jsonl(metadata_path, records)
    return metadata_path, records


def run_mock_pipelines(
    *,
    dataset_path: Path,
    audio_metadata_path: Path,
    output_dir: Path,
    run_id: str = "notebook-demo",
    limit: int | None = None,
) -> dict[str, list[PipelineRunRecord]]:
    """Run pipelines A-D with mock adapters and return records per pipeline.

    Pipeline A consumes the text dataset; B, C, and D consume audio metadata.
    Artifacts are written as one JSONL file per pipeline under ``output_dir``.
    """
    registry = default_tool_registry()
    executor = ToolExecutor(registry)
    records_by_pipeline: dict[str, list[PipelineRunRecord]] = {}
    pipelines: tuple[PipelineName, ...] = ("A", "B", "C", "D")
    for pipeline in pipelines:
        input_path = dataset_path if pipeline == "A" else audio_metadata_path
        records_by_pipeline[pipeline] = run_benchmark(
            pipeline=pipeline,
            dataset_path=input_path,
            output_path=output_dir / f"pipeline-{pipeline.lower()}.jsonl",
            run_id=run_id,
            registry=registry,
            executor=executor,
            model="mock",
            limit=limit,
        )
    return records_by_pipeline


def load_run(path: Path) -> list[PipelineRunRecord]:
    """Load pipeline run records from a JSONL artifact."""
    return read_pipeline_jsonl(path)


def records_table(records: list[PipelineRunRecord]) -> pd.DataFrame:
    """Flatten pipeline run records into a DataFrame for notebook display."""
    return pd.DataFrame(
        [
            {
                "pipeline": record.pipeline,
                "example_id": record.example_id,
                "modality": record.input_modality,
                "first_pass_parsable": record.first_pass_parsable,
                "repair_attempted": record.repair_attempted,
                "repair_success": record.repair_success,
                "validation_errors": len(record.validation_errors),
                "transcript": record.transcript,
                "wer": record.wer,
                "final_answer": record.final_answer,
            }
            for record in records
        ]
    )


def parsed_envelope(
    records: list[PipelineRunRecord], example_id: str
) -> dict[str, Any] | None:
    """Return the parsed JSON envelope for one example, or None when invalid."""
    record = next(
        (record for record in records if record.example_id == example_id), None
    )
    return None if record is None else record.parsed_output


def metrics_summary(
    *,
    examples: list[BenchmarkExample],
    records_by_pipeline: dict[str, list[PipelineRunRecord]],
) -> pd.DataFrame:
    """Aggregate per-pipeline metrics into the contract-shaped summary table."""
    return summarize_metrics(dataset=examples, records_by_pipeline=records_by_pipeline)
