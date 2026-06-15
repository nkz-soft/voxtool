from __future__ import annotations

from typing import Any

from packages.model_runner.adapters.base import (
    AdapterCapabilities,
    ModelResponse,
    resolve_hf_token,
)


class VoxtralAdapter:
    """Import-safe adapter for the Voxtral audio+text model.

    Heavy runtime dependencies (``transformers``/``torch``) and model weights are
    loaded lazily inside :meth:`generate_text`, so importing this module and
    reading its declared :attr:`capabilities` never downloads a model. This keeps
    ordinary CI to import/config/contract checks while still allowing a real run
    in Colab or on a GPU runner. Voxtral accepts audio and text input and emits a
    transcript plus a tool-call envelope, so it can serve Pipelines A, C, and D.
    """

    model_family = "voxtral"

    def __init__(
        self,
        *,
        adapter_id: str = "voxtral",
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
            supports_audio_input=True,
            supports_transcript_output=True,
            supports_tool_call_output=True,
            supports_lora=False,
            supports_quantization=True,
            supported_pipelines=["A", "C", "D"],
        )

    def _load_runtime(self) -> Any:
        if self._runtime is not None:
            return self._runtime
        if not self._model_name:
            raise ValueError(
                "VoxtralAdapter requires a 'model_name' before generation; "
                "set it in configs/models/voxtral.yaml."
            )
        # Lazy import: heavy dependencies are only needed for real inference and
        # are intentionally absent from ordinary CI.
        from transformers import AutoModelForCausalLM, AutoTokenizer

        # Pass an HF token (from HF_TOKEN/HUGGING_FACE_HUB_TOKEN) so gated models
        # like Voxtral download without an interactive login; None falls back to
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
            return ModelResponse(error=f"voxtral load failed: {exc}")

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
