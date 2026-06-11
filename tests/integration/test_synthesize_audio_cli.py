from pathlib import Path

from apps.cli.__main__ import app
from packages.tts_synth.io import read_jsonl
from typer.testing import CliRunner


def test_audio_synthesize_cli_writes_audio_and_metadata(tmp_path: Path) -> None:
    dataset = Path("data/fixtures/examples.small.jsonl")
    output = tmp_path / "audio"
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "audio",
            "synthesize",
            "--dataset",
            str(dataset),
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 0, result.output
    metadata = output / "audio.jsonl"
    assert metadata.exists()
    records = read_jsonl(metadata)
    assert len(records) == 6
    assert all(Path(record.audio_path).exists() for record in records)
    assert records[0].reference_transcript == "Convert 2 kilometer to meter."
    assert "wrote 6 audio examples" in result.output
