from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from apps.notebook.colab_demo_helpers import (
    compare_models,
    demo_dataset,
    record_summary,
    run_all_pipelines,
    run_text_demo,
    synthesize_demo_audio,
)
from packages.model_runner.adapters.base import ModelResponse
from packages.model_runner.adapters.mock import MockModelAdapter
from packages.pipeline_runner.artifacts import read_pipeline_jsonl
from packages.pipeline_runner.runner import _AdapterBridge, run_benchmark
from packages.tool_schema.providers import ToolExecutor
from packages.tool_schema.units import default_tool_registry

FIXTURE = Path("data/fixtures/advanced/sample_text.jsonl")


class _ReleasableMockAdapter(MockModelAdapter):
    def __init__(self) -> None:
        super().__init__(adapter_id="qwen")
        self.unloaded = False

    def unload_runtime(self) -> None:
        self.unloaded = True


class _FencedJsonAdapter(MockModelAdapter):
    def generate_text(
        self, prompt: str, config: dict[str, Any] | None = None
    ) -> ModelResponse:
        response = super().generate_text(prompt, config)
        response.raw_output = f"```json\n{response.raw_output}\n```"
        return response


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


def test_record_summary_distinguishes_repaired_json_from_first_pass_json() -> None:
    records = run_text_demo(
        _FencedJsonAdapter(),
        ["Convert 2 kilometers to meters."],
        run_id="fenced-json",
    )

    summary = record_summary(records[0])

    assert summary["parsable"] is True
    assert summary["first_pass_parsable"] is False
    assert summary["repair_attempted"] is True
    assert summary["repair_success"] is True


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


def test_run_benchmark_releases_real_adapter_runtime(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "run.jsonl"
    registry = default_tool_registry()
    adapter = _ReleasableMockAdapter()

    monkeypatch.setattr(
        "packages.pipeline_runner.runner.build_adapter",
        lambda *_args, **_kwargs: adapter,
    )

    run_benchmark(
        pipeline="A",
        dataset_path=FIXTURE,
        output_path=output,
        run_id="real-run",
        registry=registry,
        executor=ToolExecutor(registry),
        model="qwen",
        limit=1,
    )

    assert adapter.unloaded


def test_run_all_pipelines_can_exclude_pipeline_a(tmp_path: Path) -> None:
    dataset = demo_dataset()
    audio_examples = synthesize_demo_audio(dataset, output_dir=tmp_path / "audio")

    records, skips = run_all_pipelines(
        MockModelAdapter(),
        dataset,
        audio_examples,
        pipelines=("B", "D"),
    )

    assert set(records) == {"B", "D"}
    assert "A" not in records
    assert "A" not in skips


def test_compare_models_releases_adapter_after_each_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    adapter = _ReleasableMockAdapter()

    monkeypatch.setattr(
        "apps.notebook.colab_demo_helpers.select_adapter",
        lambda *_args, **_kwargs: adapter,
    )

    _records, comparison = compare_models(["qwen"], dataset=demo_dataset()[:1])

    assert adapter.unloaded
    assert comparison.loc[0, "model"] == "qwen"
