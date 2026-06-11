from pathlib import Path

from packages.model_runner.asr import MockASRAdapter
from packages.pipeline_runner.pipeline_b import run_pipeline_b
from packages.tts_synth.models import AudioExample, SynthesisSettings


def test_pipeline_b_runs_audio_examples_and_records_wer(tmp_path: Path) -> None:
    examples = [
        AudioExample(
            audio_id="v1-en-length-0001-audio",
            example_id="v1-en-length-0001",
            dataset_version="v1",
            language="en",
            split="test",
            reference_transcript="Convert two kilometers to meters.",
            audio_path=str(tmp_path / "v1-en-length-0001-audio.wav"),
            tts_engine="fixture-silent",
            voice="en-fixture",
            sample_rate_hz=16_000,
            duration_ms=250,
            synthesis_settings=SynthesisSettings(duration_ms=250),
        ),
        AudioExample(
            audio_id="v1-ru-length-0001-audio",
            example_id="v1-ru-length-0001",
            dataset_version="v1",
            language="ru",
            split="test",
            reference_transcript="Переведи два километра в метры.",
            audio_path=str(tmp_path / "v1-ru-length-0001-audio.wav"),
            tts_engine="fixture-silent",
            voice="ru-fixture",
            sample_rate_hz=16_000,
            duration_ms=250,
            synthesis_settings=SynthesisSettings(duration_ms=250),
        ),
    ]
    adapter = MockASRAdapter(
        transcript_overrides={
            "v1-ru-length-0001-audio": "переведи два метра",
        }
    )

    records = run_pipeline_b(
        examples,
        run_id="smoke-002",
        asr_adapter=adapter,
        output_path=tmp_path / "pipeline-b.jsonl",
    )

    assert len(records) == 2
    assert records[0].pipeline == "B"
    assert records[0].input_modality == "audio"
    assert records[0].transcript == "Convert two kilometers to meters."
    assert records[0].raw_output == "Convert two kilometers to meters."
    assert records[0].wer == 0
    assert records[1].transcript == "переведи два метра"
    assert records[1].wer == 0.6
    assert (tmp_path / "pipeline-b.jsonl").exists()
