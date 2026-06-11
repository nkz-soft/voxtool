from __future__ import annotations

from pathlib import Path
from typing import Literal

from packages.dataset_builder.io import read_jsonl
from packages.model_runner.asr import MockASRAdapter
from packages.model_runner.mock import MockModelAdapter
from packages.pipeline_runner.artifacts import PipelineRunRecord
from packages.pipeline_runner.pipeline_a import run_pipeline_a
from packages.pipeline_runner.pipeline_b import run_pipeline_b
from packages.tool_schema.providers import ToolExecutor, ToolRegistry
from packages.tts_synth.io import read_jsonl as read_audio_jsonl


def run_benchmark(
    *,
    pipeline: Literal["A", "B"],
    dataset_path: Path,
    output_path: Path,
    run_id: str,
    registry: ToolRegistry,
    executor: ToolExecutor,
    model: Literal["mock"] = "mock",
    limit: int | None = None,
) -> list[PipelineRunRecord]:
    """Dispatch a benchmark run for implemented pipelines."""
    if model != "mock":
        raise ValueError("Only the mock model adapter is implemented.")

    if pipeline == "A":
        examples = read_jsonl(dataset_path)
        if limit is not None:
            examples = examples[:limit]

        return run_pipeline_a(
            examples,
            run_id=run_id,
            model_adapter=MockModelAdapter(),
            registry=registry,
            executor=executor,
            output_path=output_path,
        )

    if pipeline == "B":
        audio_examples = read_audio_jsonl(dataset_path)
        if limit is not None:
            audio_examples = audio_examples[:limit]

        return run_pipeline_b(
            audio_examples,
            run_id=run_id,
            asr_adapter=MockASRAdapter(),
            output_path=output_path,
        )

    raise ValueError(f"Unsupported pipeline: {pipeline}")
