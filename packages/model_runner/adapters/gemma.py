from __future__ import annotations

from typing import Any

from packages.model_runner.adapters.base import (
    AdapterCapabilities,
    ModelResponse,
    resolve_hf_token,
)


class GemmaAdapter:
    """Import-safe adapter for the Gemma text model.

    Heavy runtime dependencies (``transformers``/``torch``) and model weights are
    loaded lazily inside :meth:`generate_text`, so importing this module and
    reading its declared :attr:`capabilities` never downloads a model. Gemma is a
    text-in/tool-call-out model that supports LoRA and quantized profiles, so it
    serves Pipelines A and D.
    """

    model_family = "gemma"

    def __init__(
        self,
        *,
        adapter_id: str = "gemma",
        model_name: str | None = None,
        inference_profile: str | None = None,
        generation: dict[str, Any] | None = None,
    ) -> None:
        self._adapter_id = adapter_id
        self._model_name = model_name
        self._inference_profile = inference_profile
        self._generation = dict(generation or {})
        self._runtime: Any = None

    @property
    def adapter_id(self) -> str:
        """Return the stable adapter identifier stored in run artifacts."""
        return self._adapter_id

    @property
    def inference_profile(self) -> str | None:
        """Return the configured inference profile identifier, if any."""
        return self._inference_profile

    @property
    def capabilities(self) -> AdapterCapabilities:
        """Return the adapter's declared input/output and runtime capabilities."""
        return AdapterCapabilities(
            supports_text_input=True,
            supports_audio_input=False,
            supports_transcript_output=False,
            supports_tool_call_output=True,
            supports_lora=True,
            supports_quantization=True,
            supported_pipelines=["A", "D"],
        )

    def _load_runtime(self) -> Any:
        if self._runtime is not None:
            return self._runtime
        if not self._model_name:
            raise ValueError(
                "GemmaAdapter requires a 'model_name' before generation; "
                "set it in configs/models/gemma.yaml."
            )
        # Lazy import: heavy dependencies are only needed for real inference and
        # are intentionally absent from ordinary CI.
        from transformers import AutoModelForCausalLM, AutoTokenizer

        # Pass an HF token (from HF_TOKEN/HUGGING_FACE_HUB_TOKEN) so gated models
        # like Gemma download without an interactive login; None falls back to
        # any cached huggingface_hub.login token.
        token = resolve_hf_token()
        tokenizer = AutoTokenizer.from_pretrained(self._model_name, token=token)
        model = AutoModelForCausalLM.from_pretrained(self._model_name, token=token)
        self._runtime = (tokenizer, model)
        return self._runtime

    def generate_text(
        self, prompt: str, config: dict[str, Any] | None = None
    ) -> ModelResponse:
        """Generate one raw model response for a text prompt.

        Parsing and schema validation remain the pipeline's responsibility, so
        the returned ``raw_output`` is exactly what the model produced.
        """
        try:
            tokenizer, model = self._load_runtime()
        except Exception as exc:  # noqa: BLE001 - surface load failures as data
            return ModelResponse(error=f"gemma load failed: {exc}")

        options = {**self._generation, **(config or {})}
        inputs = tokenizer(prompt, return_tensors="pt")
        outputs = model.generate(**inputs, **options)
        text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return ModelResponse(
            raw_output=text,
            metadata={
                "adapter_id": self._adapter_id,
                "model_name": self._model_name,
                "inference_profile": self._inference_profile,
            },
        )
