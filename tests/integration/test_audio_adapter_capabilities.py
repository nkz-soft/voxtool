from __future__ import annotations

from pathlib import Path

import pytest
from packages.model_runner.adapters.base import AdapterCapabilities
from packages.model_runner.adapters.mock import MockModelAdapter
from packages.pipeline_runner.capabilities import (
    AdapterPipelineSkip,
    check_adapter_for_pipeline,
    ensure_adapter_supports,
)
from packages.pipeline_runner.runner import run_benchmark
from packages.tool_schema.providers import ToolExecutor
from packages.tool_schema.units import default_tool_registry


def _audio_adapter() -> MockModelAdapter:
    return MockModelAdapter(
        adapter_id="mock-audio",
        capabilities=AdapterCapabilities(
            supports_text_input=True,
            supports_audio_input=True,
            supports_transcript_output=True,
            supports_tool_call_output=True,
            supported_pipelines=["A", "C", "D"],
        ),
    )


def test_text_only_adapter_skipped_for_audio_pipeline_c() -> None:
    adapter = MockModelAdapter(adapter_id="mock-text")

    skip = check_adapter_for_pipeline(adapter, "C")

    assert skip is not None
    assert skip.adapter_id == "mock-text"
    assert skip.pipeline == "C"
    assert "supports_audio_input" in skip.missing_capabilities


def test_audio_adapter_supports_all_pipelines() -> None:
    adapter = _audio_adapter()

    assert check_adapter_for_pipeline(adapter, "A") is None
    assert check_adapter_for_pipeline(adapter, "C") is None
    assert check_adapter_for_pipeline(adapter, "D") is None


def test_ensure_adapter_supports_raises_structured_skip() -> None:
    adapter = MockModelAdapter(adapter_id="mock-text")

    with pytest.raises(AdapterPipelineSkip) as exc_info:
        ensure_adapter_supports(adapter, "C")

    assert exc_info.value.skip.pipeline == "C"
    assert "supports_audio_input" in exc_info.value.skip.missing_capabilities


def test_run_benchmark_skips_text_adapter_on_audio_pipeline(tmp_path: Path) -> None:
    registry = default_tool_registry()

    with pytest.raises(AdapterPipelineSkip):
        run_benchmark(
            pipeline="C",
            dataset_path=tmp_path / "unused.jsonl",
            output_path=tmp_path / "out.jsonl",
            run_id="skip-run",
            registry=registry,
            executor=ToolExecutor(registry),
            model="qwen",
        )
