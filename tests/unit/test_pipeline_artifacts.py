import json
from pathlib import Path

from packages.pipeline_runner.artifacts import PipelineRunRecord, write_pipeline_jsonl
from packages.tool_schema.providers import StructuredToolFailure, ToolResult


def test_artifact_writer_serializes_pipeline_records(tmp_path: Path) -> None:
    record = PipelineRunRecord(
        run_id="smoke-001",
        pipeline="A",
        example_id="ex-001",
        dataset_version="v1",
        model_adapter="MockModelAdapter",
        input_modality="text",
        raw_output="not-json",
        parsed_output=None,
        first_pass_parsable=False,
        repair_attempted=True,
        repair_success=False,
        validation_errors=["Invalid JSON"],
        structured_failures=[
            StructuredToolFailure(
                failure_type="unknown_tool",
                tool="weather.lookup",
                message="Tool is not registered.",
                details={"available_tools": ["units.convert"]},
                stage="registry",
            )
        ],
        transcript=None,
        tool_execution_result=ToolResult(
            tool="units.convert",
            arguments={"value": 2, "from_unit": "kilometer", "to_unit": "meter"},
            result={"result_value": 2000, "result_unit": "meter"},
        ),
        final_answer="2 kilometers is 2000 meters.",
    )

    output = tmp_path / "pipeline.jsonl"
    count = write_pipeline_jsonl(output, [record])

    assert count == 1
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["run_id"] == "smoke-001"
    assert payload["pipeline"] == "A"
    assert payload["validation_errors"] == ["Invalid JSON"]
    assert payload["structured_failures"][0]["failure_type"] == "unknown_tool"
    assert payload["tool_execution_result"]["success"] is True
