from __future__ import annotations

from pathlib import Path
from typing import Any

from packages.dataset_builder.models import BenchmarkExample
from packages.model_runner.adapters.base import ModelAdapter
from packages.model_runner.adapters.mock import MockModelAdapter
from packages.model_runner.registry import available_adapters, build_adapter
from packages.pipeline_runner.artifacts import PipelineRunRecord
from packages.pipeline_runner.capabilities import check_adapter_for_pipeline
from packages.pipeline_runner.pipeline_a import run_pipeline_a
from packages.pipeline_runner.runner import _AdapterBridge
from packages.tool_schema.providers import ToolExecutor
from packages.tool_schema.units import default_tool_registry

# Stable list of adapters a Colab user can select in the demo notebook. The mock
# adapter requires no download and runs anywhere; the real adapters fetch weights
# lazily on first use and need GPU/Colab resources.
SELECTABLE_ADAPTERS: tuple[str, ...] = tuple(available_adapters())


def list_adapters() -> list[str]:
    """Return adapter IDs the Colab demo can select."""
    return list(SELECTABLE_ADAPTERS)


def select_adapter(
    adapter_id: str, *, config_path: str | Path | None = None
) -> ModelAdapter:
    """Build an import-safe adapter by ID for the notebook.

    No model is downloaded here; real weights load lazily on the first text run.
    """
    return build_adapter(adapter_id, config_path=config_path)


def text_examples(prompts: list[str]) -> list[BenchmarkExample]:
    """Wrap raw demo prompts as Pipeline A benchmark examples.

    Demo prompts carry no expected label, so each example is marked as not
    needing a tool; the adapter's actual tool decision is still recorded by the
    pipeline run.
    """
    examples: list[BenchmarkExample] = []
    for index, prompt in enumerate(prompts, start=1):
        example_id = f"demo-{index:04d}"
        examples.append(
            BenchmarkExample(
                example_id=example_id,
                dataset_version="demo",
                language="en",
                split="test",
                unit_family="none",
                text=prompt,
                needs_tool=False,
                expected_tool_call=None,
                expected_final_answer="(demo)",
                audio_id=f"{example_id}-audio",
            )
        )
    return examples


def run_text_demo(
    adapter: ModelAdapter,
    prompts: list[str],
    *,
    run_id: str = "colab-demo",
    output_path: Path | None = None,
) -> list[PipelineRunRecord]:
    """Run Pipeline A over demo prompts with the selected adapter.

    Records preserve raw output, parsed JSON, validation results, tool execution
    results, and final answers exactly like a normal benchmark run.
    """
    registry = default_tool_registry()
    executor = ToolExecutor(registry)
    skip = check_adapter_for_pipeline(adapter, "A")
    if skip is not None:
        raise ValueError(skip.reason)
    return run_pipeline_a(
        text_examples(prompts),
        run_id=run_id,
        model_adapter=_AdapterBridge(adapter),
        registry=registry,
        executor=executor,
        output_path=output_path,
    )


def demo_mock_adapter() -> MockModelAdapter:
    """Return the deterministic mock adapter for a no-download dry run."""
    return MockModelAdapter()


def record_summary(record: PipelineRunRecord) -> dict[str, Any]:
    """Flatten one run record into the fields the notebook displays."""
    tool_result = record.tool_execution_result
    return {
        "example_id": record.example_id,
        "raw_output": record.raw_output,
        "parsable": record.first_pass_parsable,
        "validation_errors": record.validation_errors,
        "tool": tool_result.tool if tool_result is not None else None,
        "tool_result": tool_result.result if tool_result is not None else None,
        "final_answer": record.final_answer,
    }
