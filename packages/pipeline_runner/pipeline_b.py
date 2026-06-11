from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from packages.asr_eval.wer import calculate_wer
from packages.model_runner.asr import ASRAdapter
from packages.pipeline_runner.artifacts import PipelineRunRecord, write_pipeline_jsonl
from packages.tts_synth.models import AudioExample


def run_pipeline_b(
    examples: Iterable[AudioExample],
    *,
    run_id: str,
    asr_adapter: ASRAdapter,
    output_path: Path | None = None,
) -> list[PipelineRunRecord]:
    """Run Pipeline B over audio examples and optionally persist artifacts."""
    records = [
        _run_one_audio_example(
            example,
            run_id=run_id,
            asr_adapter=asr_adapter,
        )
        for example in examples
    ]
    if output_path is not None:
        write_pipeline_jsonl(output_path, records)
    return records


def _run_one_audio_example(
    example: AudioExample,
    *,
    run_id: str,
    asr_adapter: ASRAdapter,
) -> PipelineRunRecord:
    transcript = asr_adapter.transcribe(example)
    transcript_wer = calculate_wer(
        example.reference_transcript,
        transcript.transcript,
    )
    return PipelineRunRecord(
        run_id=run_id,
        pipeline="B",
        example_id=example.example_id,
        dataset_version=example.dataset_version,
        model_adapter=transcript.adapter_name,
        input_modality="audio",
        raw_output=transcript.transcript,
        parsed_output=None,
        first_pass_parsable=True,
        repair_attempted=False,
        repair_success=False,
        validation_errors=[],
        structured_failures=[],
        transcript=transcript.transcript,
        wer=transcript_wer,
        tool_execution_result=None,
        final_answer=transcript.transcript,
    )
