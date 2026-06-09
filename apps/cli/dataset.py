"""CLI commands for deterministic benchmark dataset generation."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from packages.dataset_builder import generate_dataset, write_jsonl

app = typer.Typer(help="Dataset generation commands.")


@app.command()
def generate(
    version: Annotated[
        str,
        typer.Option("--version", help="Dataset version identifier."),
    ],
    output: Annotated[Path, typer.Option("--output", help="Output JSONL path.")],
) -> None:
    """Generate the deterministic bilingual benchmark dataset."""
    examples = generate_dataset(version=version)
    count = write_jsonl(output, examples)
    typer.echo(f"wrote {count} dataset examples to {output}")
