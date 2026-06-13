import json
from pathlib import Path
from typing import Any

from packages.pipeline_runner.artifacts import (
    PipelineRunRecord,
    SpeechOutputArtifact,
    read_pipeline_jsonl,
    write_pipeline_jsonl,
)
from packages.tool_schema.providers import ToolManifest


def _base_record(**overrides: Any) -> PipelineRunRecord:
    record = PipelineRunRecord(
        run_id="advanced-smoke",
        pipeline="A",
        example_id="ex-001",
        dataset_version="advanced-v1",
        model_adapter="MockModelAdapter",
        input_modality="text",
        raw_output='{"needs_tool": false, "tool_call": null}',
        parsed_output={"needs_tool": False, "tool_call": None},
        first_pass_parsable=True,
        repair_attempted=False,
        repair_success=False,
    )
    return record.model_copy(update=overrides) if overrides else record


def test_existing_records_default_advanced_fields() -> None:
    record = _base_record()

    assert record.adapter_id is None
    assert record.adapter_capabilities is None
    assert record.inference_profile is None
    assert record.tool_manifest_snapshot == []
    assert record.speech_output is None
    assert record.runtime_skip_reason is None


def test_advanced_fields_round_trip_through_jsonl(tmp_path: Path) -> None:
    record = _base_record(
        adapter_id="qwen",
        adapter_capabilities={
            "supports_text_input": True,
            "supports_audio_input": False,
            "supports_tool_call_output": True,
        },
        inference_profile="quantized_4bit",
        tool_manifest_snapshot=[
            ToolManifest(
                name="units.convert",
                description="Convert units.",
                arguments_json_schema={},
            )
        ],
        speech_output=SpeechOutputArtifact(
            generation_status="generated",
            speech_output_path="runs/advanced-smoke/audio/ex-001.wav",
            speech_provider="mock",
        ),
    )

    output = tmp_path / "advanced.jsonl"
    count = write_pipeline_jsonl(output, [record])

    assert count == 1
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["adapter_id"] == "qwen"
    assert payload["adapter_capabilities"]["supports_text_input"] is True
    assert payload["inference_profile"] == "quantized_4bit"
    assert payload["tool_manifest_snapshot"][0]["name"] == "units.convert"
    assert payload["speech_output"]["generation_status"] == "generated"

    restored = read_pipeline_jsonl(output)
    assert restored[0].speech_output is not None
    assert restored[0].speech_output.speech_provider == "mock"


def test_runtime_skip_is_distinct_from_model_failure() -> None:
    record = _base_record(
        raw_output="",
        first_pass_parsable=False,
        runtime_skip_reason=(
            "Adapter 'qwen' cannot run pipeline C: missing supports_audio_input."
        ),
    )

    assert record.runtime_skip_reason is not None
    assert record.validation_errors == []
    assert record.structured_failures == []


def test_speech_output_can_record_failure_without_path() -> None:
    artifact = SpeechOutputArtifact(
        generation_status="failed",
        generation_error="synthesizer unavailable",
    )

    assert artifact.speech_output_path is None
    assert artifact.generation_status == "failed"
    assert artifact.generation_error == "synthesizer unavailable"
