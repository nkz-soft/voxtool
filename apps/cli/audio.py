"""CLI commands for deterministic audio fixture synthesis."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from packages.dataset_builder import read_jsonl as read_dataset_jsonl
from packages.tts_synth import SynthesisSettings, synthesize_dataset, write_jsonl

app = typer.Typer(help="Audio synthesis commands.")


@app.command()
def synthesize(
    dataset: Annotated[
        Path,
        typer.Option("--dataset", help="Input benchmark dataset JSONL path."),
    ],
    output: Annotated[
        Path,
        typer.Option("--output", help="Output directory for audio and metadata."),
    ],
    sample_rate_hz: Annotated[
        int,
        typer.Option("--sample-rate-hz", help="Fixture WAV sample rate."),
    ] = 16_000,
    duration_ms: Annotated[
        int,
        typer.Option("--duration-ms", help="Fixture WAV duration in milliseconds."),
    ] = 1000,
) -> None:
    """Generate deterministic local audio fixtures and metadata."""
    examples = read_dataset_jsonl(dataset)
    settings = SynthesisSettings(
        engine="fixture-silent",
        sample_rate_hz=sample_rate_hz,
        duration_ms=duration_ms,
    )
    records = synthesize_dataset(examples, output_dir=output, settings=settings)
    metadata_path = output / "audio.jsonl"
    count = write_jsonl(metadata_path, records)
    typer.echo(f"wrote {count} audio examples to {metadata_path}")
