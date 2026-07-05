from __future__ import annotations

from typing import Any

from packages.model_runner.adapters.base import (
    AdapterCapabilities,
    ModelResponse,
    clear_cuda_memory,
    cuda_is_available,
    generated_token_ids,
    move_inputs_to_runtime_device,
    real_model_load_kwargs,
    release_adapter_resources,
    release_runtime_objects,
    resolve_hf_token,
)

_VOXTRAL_TEXT_CHAT_TEMPLATE = (
    "{% for message in messages %}"
    "{% if message['role'] == 'user' %}"
    "{{ bos_token + '[INST] ' + message['content'] | trim + ' [/INST]' }}"
    "{% elif message['role'] == 'assistant' %}"
    "{{ ' ' + message['content'] | trim + eos_token }}"
    "{% endif %}"
    "{% endfor %}"
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
        clear_cuda_memory()
        # Lazy import: heavy dependencies are only needed for real inference and
        # are intentionally absent from ordinary CI.
        from transformers import AutoProcessor, VoxtralForConditionalGeneration

        # Pass an HF token (from HF_TOKEN/HUGGING_FACE_HUB_TOKEN) so gated models
        # like Voxtral download without an interactive login; None falls back to
        # any cached huggingface_hub.login token. On GPU runtimes, load with
        # Accelerate's automatic device map so Kaggle/Colab CUDA is used.
        token = resolve_hf_token()
        processor = AutoProcessor.from_pretrained(self._model_name, token=token)
        model = VoxtralForConditionalGeneration.from_pretrained(
            self._model_name, **real_model_load_kwargs()
        )
        self._runtime = (processor, model)
        return self._runtime

    def unload_runtime(self) -> None:
        """Drop cached processor/model objects so GPU memory can be reclaimed."""
        release_runtime_objects(self._runtime)
        self._runtime = None

    def _tokenize_text_prompt(self, processor: Any, prompt: str) -> Any:
        """Tokenize text through Voxtral's chat path."""
        self._ensure_padding_token(processor)
        if not hasattr(processor, "apply_chat_template"):
            raise ValueError(
                "Voxtral processor must provide apply_chat_template for generation."
            )

        messages = [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            }
        ]
        try:
            return processor.apply_chat_template(
                messages,
                return_tensors="pt",
                return_dict=True,
            )
        except ValueError as exc:
            if "chat_template" not in str(exc):
                raise

        self._set_default_text_chat_template(processor)
        return processor.apply_chat_template(
            [{"role": "user", "content": prompt}],
            return_tensors="pt",
            return_dict=True,
        )

    def _set_default_text_chat_template(self, processor: Any) -> None:
        """Install a text chat template for processors that do not ship one."""
        for target in (processor, getattr(processor, "tokenizer", None)):
            if target is None:
                continue
            try:
                target.chat_template = _VOXTRAL_TEXT_CHAT_TEMPLATE
            except AttributeError:
                continue

    def _ensure_padding_token(self, processor: Any) -> None:
        """Use EOS as padding token when the processor tokenizer has none."""
        tokenizer = getattr(processor, "tokenizer", processor)
        if getattr(tokenizer, "pad_token", None) is not None:
            return

        eos_token = getattr(tokenizer, "eos_token", None)
        if eos_token is not None:
            tokenizer.pad_token = eos_token
            return

        eos_token_id = getattr(tokenizer, "eos_token_id", None)
        if eos_token_id is not None:
            tokenizer.pad_token_id = eos_token_id

    def generate_text(
        self, prompt: str, config: dict[str, Any] | None = None
    ) -> ModelResponse:
        """Generate one raw model response for a text prompt.

        Parsing and schema validation remain the pipeline's responsibility, so
        the returned ``raw_output`` is exactly what the model produced.
        """
        try:
            processor, model = self._load_runtime()
        except Exception as exc:  # noqa: BLE001 - surface load failures as data
            release_adapter_resources(self)
            return ModelResponse(error=f"voxtral load failed: {exc}")

        options = {**self._generation, **(config or {})}
        inputs = self._tokenize_text_prompt(processor, prompt)
        inputs = move_inputs_to_runtime_device(inputs)
        outputs = model.generate(**inputs, **options)
        output_ids = outputs[0]
        if hasattr(output_ids, "detach"):
            output_ids = output_ids.detach().cpu()
        completion_ids = generated_token_ids(output_ids, inputs)
        text = processor.decode(completion_ids, skip_special_tokens=True)
        return ModelResponse(
            raw_output=text,
            metadata={
                "adapter_id": self._adapter_id,
                "model_name": self._model_name,
                "inference_profile": self._inference_profile,
                "cuda_available": cuda_is_available(),
            },
        )
