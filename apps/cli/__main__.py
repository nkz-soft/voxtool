from __future__ import annotations

from pathlib import Path

import typer

from apps.cli import benchmark, dataset

app = typer.Typer(help="VoxTool benchmark and demo CLI.")
app.add_typer(dataset.app, name="dataset")
app.add_typer(benchmark.app, name="benchmark")


@app.command()
def text(request: str) -> None:
    """Accept a text request for future benchmark/demo processing."""
    typer.echo(f"text request accepted: {request}")


@app.command()
def audio(path: Path) -> None:
    """Accept an audio path for future benchmark/demo processing."""
    typer.echo(f"audio request accepted: {path}")


if __name__ == "__main__":
    app()
