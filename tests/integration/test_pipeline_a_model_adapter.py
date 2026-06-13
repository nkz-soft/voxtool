from __future__ import annotations

from pathlib import Path

from apps.notebook.colab_demo_helpers import run_text_demo
from packages.model_runner.adapters.mock import MockModelAdapter
from packages.pipeline_runner.artifacts import read_pipeline_jsonl
from packages.pipeline_runner.runner import _AdapterBridge, run_benchmark
from packages.tool_schema.providers import ToolExecutor
from packages.tool_schema.units import default_tool_registry

FIXTURE = Path("data/fixtures/advanced/sample_text.jsonl")


def test_mock_adapter_runs_pipeline_a_through_bridge(tmp_path: Path) -> None:
    output = tmp_path / "pipeline-a.jsonl"
    records = run_text_demo(
        MockModelAdapter(),
        ["Convert 2 kilometers to meters."],
        run_id="adapter-it",
        output_path=output,
    )

    assert len(records) == 1
    record = records[0]
    # Artifacts preserved: raw output, parsed JSON, validation, execution, answer.
    assert record.raw_output
    assert record.first_pass_parsable
    assert record.validation_errors == []
    assert record.tool_execution_result is not None
    assert record.tool_execution_result.tool == "units.convert"
    assert record.final_answer is not None
    assert output.exists()


def test_bridge_preserves_adapter_id_as_model_adapter_name() -> None:
    bridge = _AdapterBridge(MockModelAdapter(adapter_id="mock"))

    output = bridge.generate_text("Convert 2 kilometers to meters.")

    assert output.adapter_name == "mock"
    assert "units.convert" in output.raw_output


def test_run_benchmark_mock_pipeline_a_preserves_artifacts(tmp_path: Path) -> None:
    output = tmp_path / "run.jsonl"
    registry = default_tool_registry()

    records = run_benchmark(
        pipeline="A",
        dataset_path=FIXTURE,
        output_path=output,
        run_id="mock-run",
        registry=registry,
        executor=ToolExecutor(registry),
        model="mock",
        limit=2,
    )

    assert len(records) == 2
    reloaded = read_pipeline_jsonl(output)
    assert [r.example_id for r in reloaded] == [r.example_id for r in records]
    assert all(r.model_adapter == "MockModelAdapter" for r in reloaded)
