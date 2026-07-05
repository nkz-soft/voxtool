"""CLI commands for benchmark audio synthesis."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from packages.dataset_builder import read_jsonl as read_dataset_jsonl
from packages.tts_synth import (
    SynthesisError,
    SynthesisSettings,
    synthesize_dataset,
    write_jsonl,
)

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
        typer.Option("--sample-rate-hz", help="Requested WAV sample rate metadata."),
    ] = 16_000,
    duration_ms: Annotated[
        int,
        typer.Option("--duration-ms", help="Fixture WAV duration in milliseconds."),
    ] = 1000,
    engine: Annotated[
        str,
        typer.Option("--engine", help="TTS engine: fixture-silent or piper."),
    ] = "fixture-silent",
    voice: Annotated[
        str | None,
        typer.Option("--voice", help="Logical Piper voice name for metadata."),
    ] = None,
    voice_model_path: Annotated[
        Path | None,
        typer.Option("--voice-model-path", help="Local Piper .onnx voice path."),
    ] = None,
    voice_config_path: Annotated[
        Path | None,
        typer.Option("--voice-config-path", help="Local Piper .onnx.json config path."),
    ] = None,
) -> None:
    """Generate local benchmark audio and complete metadata."""
    examples = read_dataset_jsonl(dataset)
    settings = SynthesisSettings(
        engine=engine,
        sample_rate_hz=sample_rate_hz,
        duration_ms=duration_ms,
        voice=voice,
        voice_model_path=voice_model_path,
        voice_config_path=voice_config_path,
    )
    try:
        records = synthesize_dataset(examples, output_dir=output, settings=settings)
    except (SynthesisError, RuntimeError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    metadata_path = output / "audio.jsonl"
    count = write_jsonl(metadata_path, records)
    typer.echo(f"wrote {count} audio examples to {metadata_path}")
