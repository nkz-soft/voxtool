from __future__ import annotations

from pathlib import Path
from typing import Literal

from packages.dataset_builder.io import read_jsonl
from packages.model_runner.adapters.base import ModelAdapter, ModelResponse
from packages.model_runner.asr import MockASRAdapter
from packages.model_runner.base import ModelOutput
from packages.model_runner.mock import MockModelAdapter
from packages.model_runner.registry import build_adapter
from packages.pipeline_runner.artifacts import PipelineRunRecord, write_pipeline_jsonl
from packages.pipeline_runner.capabilities import ensure_adapter_supports
from packages.pipeline_runner.pipeline_a import run_pipeline_a
from packages.pipeline_runner.pipeline_b import run_pipeline_b
from packages.pipeline_runner.pipeline_c import run_pipeline_c
from packages.pipeline_runner.pipeline_d import run_pipeline_d
from packages.tool_schema.providers import ToolExecutor, ToolRegistry
from packages.tts_synth.io import read_jsonl as read_audio_jsonl


class _AdapterBridge:
    """Adapt a ``ModelAdapter`` to the legacy ``TextModelAdapter`` surface.

    The advanced adapters return a :class:`ModelResponse` while the pipelines
    consume the ``generate_text(prompt) -> ModelOutput`` surface. The bridge
    preserves the exact raw output (or the adapter error text when generation
    failed before producing output) so downstream parsing, validation, tool
    execution, and artifact logging are unchanged for real adapters.
    """

    def __init__(self, adapter: ModelAdapter) -> None:
        self._adapter = adapter
        self.name = adapter.adapter_id

    def generate_text(self, prompt: str) -> ModelOutput:
        """Generate text via the wrapped adapter and return a ``ModelOutput``."""
        response: ModelResponse = self._adapter.generate_text(prompt)
        raw = response.raw_output or response.error or "<empty>"
        return ModelOutput(raw_output=raw, adapter_name=self.name)


def _enrich_with_adapter(
    records: list[PipelineRunRecord], adapter: ModelAdapter
) -> list[PipelineRunRecord]:
    """Attach adapter identity, capabilities, and profile to real-adapter runs."""
    capabilities = adapter.capabilities.model_dump(mode="json")
    inference_profile = getattr(adapter, "inference_profile", None)
    return [
        record.model_copy(
            update={
                "adapter_id": adapter.adapter_id,
                "adapter_capabilities": capabilities,
                "inference_profile": inference_profile,
            }
        )
        for record in records
    ]


def run_benchmark(
    *,
    pipeline: Literal["A", "B", "C", "D"],
    dataset_path: Path,
    output_path: Path,
    run_id: str,
    registry: ToolRegistry,
    executor: ToolExecutor,
    model: str = "mock",
    config_path: Path | None = None,
    limit: int | None = None,
) -> list[PipelineRunRecord]:
    """Dispatch a benchmark run for implemented pipelines.

    ``model`` selects the adapter: ``"mock"`` uses the deterministic in-process
    adapter, while ``"voxtral"``, ``"qwen"``, and ``"gemma"`` are built from the
    adapter registry. Real adapters are capability-checked before any model run,
    and the resulting records carry the adapter ID, capabilities, and profile.
    """
    use_real_adapter = model != "mock"
    real_adapter: ModelAdapter | None = None
    if use_real_adapter:
        real_adapter = build_adapter(model, config_path=config_path)
        if pipeline in ("A", "C", "D"):
            ensure_adapter_supports(real_adapter, pipeline)
        text_adapter: object = _AdapterBridge(real_adapter)
    else:
        text_adapter = MockModelAdapter()

    if pipeline == "A":
        examples = read_jsonl(dataset_path)
        if limit is not None:
            examples = examples[:limit]

        records = run_pipeline_a(
            examples,
            run_id=run_id,
            model_adapter=text_adapter,  # type: ignore[arg-type]
            registry=registry,
            executor=executor,
            output_path=None if use_real_adapter else output_path,
        )
    elif pipeline == "B":
        audio_examples = read_audio_jsonl(dataset_path)
        if limit is not None:
            audio_examples = audio_examples[:limit]

        return run_pipeline_b(
            audio_examples,
            run_id=run_id,
            asr_adapter=MockASRAdapter(),
            output_path=output_path,
        )
    elif pipeline == "C":
        audio_examples = read_audio_jsonl(dataset_path)
        if limit is not None:
            audio_examples = audio_examples[:limit]

        records = run_pipeline_c(
            audio_examples,
            run_id=run_id,
            model_adapter=text_adapter,  # type: ignore[arg-type]
            registry=registry,
            executor=executor,
            output_path=None if use_real_adapter else output_path,
        )
    elif pipeline == "D":
        audio_examples = read_audio_jsonl(dataset_path)
        if limit is not None:
            audio_examples = audio_examples[:limit]

        records = run_pipeline_d(
            audio_examples,
            run_id=run_id,
            asr_adapter=MockASRAdapter(),
            text_adapter=text_adapter,  # type: ignore[arg-type]
            registry=registry,
            executor=executor,
            output_path=None if use_real_adapter else output_path,
        )
    else:
        raise ValueError(f"Unsupported pipeline: {pipeline}")

    if use_real_adapter and real_adapter is not None:
        records = _enrich_with_adapter(records, real_adapter)
        write_pipeline_jsonl(output_path, records)
    return records
