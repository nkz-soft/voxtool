from __future__ import annotations

import os
from importlib import import_module
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


def cuda_is_available() -> bool:
    """Return True when PyTorch can see a CUDA device.

    Heavy model dependencies are optional in CI, so this helper imports torch
    lazily and treats missing torch as no CUDA support.
    """
    try:
        torch = import_module("torch")
    except Exception:  # noqa: BLE001 - torch is optional outside real runs
        return False
    return bool(torch.cuda.is_available())


def real_model_load_kwargs() -> dict[str, Any]:
    """Return shared ``from_pretrained`` kwargs for real adapter model loading."""
    kwargs: dict[str, Any] = {"token": resolve_hf_token()}
    if cuda_is_available():
        kwargs.update({"device_map": "auto", "torch_dtype": "auto"})
    return kwargs


def move_inputs_to_runtime_device(inputs: Any) -> Any:
    """Move tokenized tensors to CUDA when a GPU runtime is available."""
    if cuda_is_available() and hasattr(inputs, "to"):
        return inputs.to("cuda")
    return inputs


def generated_token_ids(output_ids: Any, inputs: Any) -> Any:
    """Return only tokens generated after the prompt prefix.

    Decoder-only Transformers models return the full prompt plus completion from
    ``generate``. Benchmark artifacts need the model completion only, otherwise
    strict JSON parsing sees the prompt instructions before the JSON envelope.
    """
    prompt_length = _input_token_count(inputs)
    if prompt_length == 0:
        return output_ids
    try:
        return output_ids[prompt_length:]
    except Exception:  # noqa: BLE001 - support tensor/list-like outputs broadly
        return output_ids


def _input_token_count(inputs: Any) -> int:
    input_ids = _input_ids(inputs)
    if input_ids is None:
        return 0

    shape = getattr(input_ids, "shape", None)
    if shape is not None and len(shape) >= 1:
        return int(shape[-1])

    size = getattr(input_ids, "size", None)
    if callable(size):
        try:
            return int(size(-1))
        except Exception:  # noqa: BLE001 - fall through to sequence handling
            pass

    try:
        first_sequence = input_ids[0]
    except Exception:  # noqa: BLE001 - final fallback for flat token sequences
        try:
            return len(input_ids)
        except Exception:  # noqa: BLE001
            return 0

    try:
        return len(first_sequence)
    except Exception:  # noqa: BLE001
        return 0


def _input_ids(inputs: Any) -> Any | None:
    if isinstance(inputs, dict):
        return inputs.get("input_ids")
    if hasattr(inputs, "get"):
        try:
            return inputs.get("input_ids")
        except Exception:  # noqa: BLE001
            pass
    return getattr(inputs, "input_ids", None)


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
