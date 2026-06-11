from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

import typer
from packages.pipeline_runner.runner import run_benchmark
from packages.tool_schema.providers import ToolExecutor
from packages.tool_schema.units import default_tool_registry

app = typer.Typer(help="Benchmark execution commands.")


@app.command()
def run(
    output: Annotated[Path, typer.Option("--output", help="Pipeline output JSONL.")],
    run_id: Annotated[str, typer.Option("--run-id", help="Benchmark run ID.")],
    dataset: Annotated[
        Path | None,
        typer.Option("--dataset", help="Input text dataset JSONL for Pipeline A."),
    ] = None,
    audio_metadata: Annotated[
        Path | None,
        typer.Option(
            "--audio-metadata",
            help="Input audio metadata JSONL for Pipeline B.",
        ),
    ] = None,
    pipeline: Annotated[
        Literal["A", "B"],
        typer.Option("--pipeline", help="Pipeline name."),
    ] = "A",
    model: Annotated[
        Literal["mock"],
        typer.Option("--model", help="Model adapter name."),
    ] = "mock",
    limit: Annotated[
        int | None,
        typer.Option("--limit", help="Optional maximum examples to run."),
    ] = None,
) -> None:
    """Run a benchmark pipeline and write PipelineRun JSONL records."""
    input_path = audio_metadata if pipeline == "B" else dataset
    if input_path is None:
        option = "--audio-metadata" if pipeline == "B" else "--dataset"
        raise typer.BadParameter(f"{option} is required for Pipeline {pipeline}")

    registry = default_tool_registry()
    records = run_benchmark(
        pipeline=pipeline,
        dataset_path=input_path,
        output_path=output,
        run_id=run_id,
        registry=registry,
        executor=ToolExecutor(registry),
        model=model,
        limit=limit,
    )
    typer.echo(f"wrote {len(records)} Pipeline {pipeline} records to {output}")
