from pathlib import Path

from packages.dataset_builder.models import BenchmarkExample
from packages.model_runner.mock import MockModelAdapter
from packages.pipeline_runner.pipeline_a import run_pipeline_a
from packages.tool_schema import ToolInvocation, ToolRegistry, UnitsConvertProvider
from packages.tool_schema.models import ToolArguments, Unit
from packages.tool_schema.providers import ToolExecutor


def test_pipeline_a_runs_text_examples_with_registry_executor_only(
    tmp_path: Path,
) -> None:
    registry = ToolRegistry([UnitsConvertProvider()])
    executor = ToolExecutor(registry)
    examples = [
        BenchmarkExample(
            example_id="v1-en-length-0001",
            dataset_version="v1",
            language="en",
            split="test",
            unit_family="length",
            text="Convert 2 kilometers to meters.",
            needs_tool=True,
            expected_tool_call=ToolInvocation(
                tool="units.convert",
                arguments=ToolArguments(
                    value=2,
                    from_unit=Unit.KILOMETER,
                    to_unit=Unit.METER,
                ),
            ),
            expected_final_answer="2 kilometers is 2000 meters.",
            audio_id="v1-en-length-0001-audio",
        ),
        BenchmarkExample(
            example_id="v1-en-none-0001",
            dataset_version="v1",
            language="en",
            split="test",
            unit_family="none",
            text="Say hello.",
            needs_tool=False,
            expected_tool_call=None,
            expected_final_answer="Hello.",
            audio_id="v1-en-none-0001-audio",
        ),
    ]

    records = run_pipeline_a(
        examples,
        run_id="smoke-001",
        model_adapter=MockModelAdapter(),
        registry=registry,
        executor=executor,
        output_path=tmp_path / "pipeline-a.jsonl",
    )

    assert len(records) == 2
    assert records[0].tool_execution_result is not None
    assert records[0].tool_execution_result.success is True
    assert records[0].structured_failures == []
    assert records[0].final_answer == "2 kilometers is 2000 meters."
    assert records[1].tool_execution_result is None
    assert records[1].final_answer == "No conversion needed."
    assert (tmp_path / "pipeline-a.jsonl").exists()
