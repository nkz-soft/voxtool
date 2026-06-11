from pathlib import Path

from packages.model_runner.asr import ASRTranscript, MockASRAdapter
from packages.tts_synth.models import AudioExample, SynthesisSettings


def _audio_example() -> AudioExample:
    return AudioExample(
        audio_id="v1-en-length-0001-audio",
        example_id="v1-en-length-0001",
        dataset_version="v1",
        language="en",
        split="test",
        reference_transcript="Convert 2 kilometers to meters.",
        audio_path=str(Path("audio") / "v1-en-length-0001-audio.wav"),
        tts_engine="fixture-silent",
        voice="en-fixture",
        sample_rate_hz=16_000,
        duration_ms=250,
        synthesis_settings=SynthesisSettings(duration_ms=250),
    )


def test_mock_asr_adapter_returns_reference_transcript_by_default() -> None:
    adapter = MockASRAdapter()

    transcript = adapter.transcribe(_audio_example())

    assert transcript == ASRTranscript(
        transcript="Convert 2 kilometers to meters.",
        adapter_name="MockASRAdapter",
    )


def test_mock_asr_adapter_can_override_transcripts_by_audio_id() -> None:
    adapter = MockASRAdapter(
        transcript_overrides={"v1-en-length-0001-audio": "convert 2 kilometers"}
    )

    transcript = adapter.transcribe(_audio_example())

    assert transcript.transcript == "convert 2 kilometers"
    assert transcript.adapter_name == "MockASRAdapter"
