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
    dataset: Annotated[Path, typer.Option("--dataset", help="Input dataset JSONL.")],
    output: Annotated[Path, typer.Option("--output", help="Pipeline output JSONL.")],
    run_id: Annotated[str, typer.Option("--run-id", help="Benchmark run ID.")],
    pipeline: Annotated[
        Literal["A"],
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
    """Run a text benchmark pipeline and write PipelineRun JSONL records."""
    registry = default_tool_registry()
    records = run_benchmark(
        pipeline=pipeline,
        dataset_path=dataset,
        output_path=output,
        run_id=run_id,
        registry=registry,
        executor=ToolExecutor(registry),
        model=model,
        limit=limit,
    )
    typer.echo(f"wrote {len(records)} Pipeline {pipeline} records to {output}")
