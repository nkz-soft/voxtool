from __future__ import annotations

from packages.model_runner.adapters.base import (
    ModelAdapter,
    SkippedCapability,
    evaluate_capability,
)


class AdapterPipelineSkip(Exception):
    """Raised when an adapter cannot serve a requested pipeline.

    Carries the structured :class:`SkippedCapability` so callers can record a
    runtime skip that is distinct from a model-output failure (no model is run).
    """

    def __init__(self, skip: SkippedCapability) -> None:
        super().__init__(skip.reason)
        self.skip = skip


def check_adapter_for_pipeline(
    adapter: ModelAdapter, pipeline: str
) -> SkippedCapability | None:
    """Return a structured skip when ``adapter`` cannot serve ``pipeline``.

    Returns ``None`` when the adapter declares everything the pipeline needs, so
    callers can proceed with execution. This is the single place runners consult
    before invoking a real adapter for an audio pipeline (C/D) or text pipeline.
    """
    return evaluate_capability(
        adapter_id=adapter.adapter_id,
        capabilities=adapter.capabilities,
        pipeline=pipeline,
    )


def ensure_adapter_supports(adapter: ModelAdapter, pipeline: str) -> None:
    """Raise :class:`AdapterPipelineSkip` if ``adapter`` cannot serve ``pipeline``.

    Use this before running a real adapter so an unsupported audio adapter is
    rejected with a structured skip rather than a partial model run.
    """
    skip = check_adapter_for_pipeline(adapter, pipeline)
    if skip is not None:
        raise AdapterPipelineSkip(skip)
