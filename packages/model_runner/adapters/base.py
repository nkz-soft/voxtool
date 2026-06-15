from __future__ import annotations

import os
from typing import Any, Literal, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

Pipeline = Literal["A", "C", "D"]

# Environment variables that may carry a Hugging Face access token, in priority
# order. Real adapters pass the resolved token to ``from_pretrained`` so gated
# models (e.g. Gemma, Voxtral) can be downloaded in Colab/Kaggle without an
# interactive login. ``None`` lets ``transformers`` fall back to any cached
# ``huggingface_hub.login`` token.
_HF_TOKEN_ENV_VARS: tuple[str, ...] = ("HF_TOKEN", "HUGGING_FACE_HUB_TOKEN")


def resolve_hf_token() -> str | None:
    """Return a Hugging Face token from the environment, or None if unset."""
    for name in _HF_TOKEN_ENV_VARS:
        value = os.environ.get(name)
        if value:
            return value
    return None


# Capability flags each pipeline requires from an adapter before it may run.
# Pipeline A is text-in/tool-call-out, Pipeline C is audio-in with transcript and
# tool-call output, and Pipeline D consumes an external transcript so the adapter
# only needs text input plus tool-call output.
PIPELINE_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "A": ("supports_text_input", "supports_tool_call_output"),
    "C": (
        "supports_audio_input",
        "supports_transcript_output",
        "supports_tool_call_output",
    ),
    "D": ("supports_text_input", "supports_tool_call_output"),
}


class ModelResponse(BaseModel):
    """Canonical adapter result holding raw output and optional parse metadata.

    Parsing and schema validation happen in the pipeline, not the adapter, so
    ``raw_output`` is the exact text the model returned and is preserved for
    every completed call. ``error`` records adapter-level failures that occur
    before any output is produced.
    """

    model_config = ConfigDict(extra="forbid")

    raw_output: str = ""
    parsed_output: dict[str, Any] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class AdapterCapabilities(BaseModel):
    """Declared input/output and runtime capabilities for a model adapter."""

    model_config = ConfigDict(extra="forbid")

    supports_text_input: bool = False
    supports_audio_input: bool = False
    supports_lora: bool = False
    supports_quantization: bool = False
    supports_transcript_output: bool = False
    supports_tool_call_output: bool = False
    supported_pipelines: list[Pipeline] = Field(default_factory=list)

    def missing_for_pipeline(self, pipeline: str) -> list[str]:
        """Return capability flags this adapter lacks for ``pipeline``.

        Includes ``"supported_pipelines"`` when the pipeline is not declared,
        so declaring a pipeline without the matching flags is still rejected.
        """
        missing = [
            flag
            for flag in PIPELINE_REQUIREMENTS.get(pipeline, ())
            if not getattr(self, flag)
        ]
        if pipeline not in self.supported_pipelines:
            missing.append("supported_pipelines")
        return missing

    def satisfies_pipeline(self, pipeline: str) -> bool:
        """Return True when the adapter declares everything ``pipeline`` needs."""
        return not self.missing_for_pipeline(pipeline)


class SkippedCapability(BaseModel):
    """Structured skip recorded when an adapter cannot serve a pipeline."""

    model_config = ConfigDict(extra="forbid")

    adapter_id: str = Field(min_length=1)
    pipeline: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    missing_capabilities: list[str] = Field(default_factory=list)


def evaluate_capability(
    *,
    adapter_id: str,
    capabilities: AdapterCapabilities,
    pipeline: str,
) -> SkippedCapability | None:
    """Check an adapter against a pipeline before any model execution.

    Returns ``None`` when the adapter is suitable, or a ``SkippedCapability``
    describing the missing flags so the run can record a structured skip that is
    distinct from a model-output failure.
    """
    missing = capabilities.missing_for_pipeline(pipeline)
    if not missing:
        return None
    return SkippedCapability(
        adapter_id=adapter_id,
        pipeline=pipeline,
        reason=(
            f"Adapter {adapter_id!r} cannot run pipeline {pipeline}: "
            f"missing {', '.join(missing)}."
        ),
        missing_capabilities=missing,
    )


@runtime_checkable
class ModelAdapter(Protocol):
    """Common adapter surface for advanced phases.

    Adapters expose a stable ``adapter_id``, declared ``capabilities``, and a
    ``generate_text`` operation returning a :class:`ModelResponse`. Concrete
    real-model adapters are added in later phases; this protocol lets the
    pipeline depend on the contract rather than any implementation.
    """

    @property
    def adapter_id(self) -> str:
        """Return the stable adapter identifier stored in run artifacts."""
        ...

    @property
    def capabilities(self) -> AdapterCapabilities:
        """Return the adapter's declared capabilities."""
        ...

    def generate_text(
        self, prompt: str, config: dict[str, Any] | None = None
    ) -> ModelResponse:
        """Generate one model response for a text prompt."""
        ...
