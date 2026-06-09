from pathlib import Path

from apps.cli.__main__ import app
from packages.dataset_builder import read_jsonl
from typer.testing import CliRunner


def test_dataset_generate_cli_writes_jsonl(tmp_path: Path) -> None:
    output = tmp_path / "examples.jsonl"
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["dataset", "generate", "--version", "v1", "--output", str(output)],
    )

    assert result.exit_code == 0, result.output
    assert output.exists()
    examples = read_jsonl(output)
    assert len(examples) == 240
    assert examples[0].dataset_version == "v1"
    assert "wrote 240 dataset examples" in result.output
