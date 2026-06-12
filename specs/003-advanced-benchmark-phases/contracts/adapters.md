# Adapter Contract

## Adapter Selection

Adapters are selected by stable ID, config file, and declared capabilities.

```json
{
  "adapter_id": "qwen",
  "model_family": "qwen",
  "config_path": "configs/models/qwen.yaml",
  "inference_profile": "base",
  "capabilities": {
    "supports_text_input": true,
    "supports_audio_input": false,
    "supports_lora": true,
    "supports_transcript_output": false,
    "supports_tool_call_output": true,
    "supports_quantization": true,
    "supported_pipelines": ["A", "D"]
  }
}
```

Required behavior:

- Every adapter implements `generate_text(prompt, config) -> ModelResponse`.
- Pipeline A requires text input and tool-call output.
- Pipeline C requires audio input, transcript output, and tool-call output.
- Pipeline D requires transcript input from an ASR path plus text input and tool-call output.
- Unsupported adapter/runtime combinations must be recorded as structured skipped-capability outcomes before model execution.
- Ordinary CI must validate this contract with mocks or bounded fixtures only.

## Real Adapter Families

Required adapter IDs and files:

- `voxtral` implemented in `packages/model_runner/voice_toolbench_model_runner/adapters/voxtral.py` with `configs/models/voxtral.yaml`
- `qwen` implemented in `packages/model_runner/voice_toolbench_model_runner/adapters/qwen.py` with `configs/models/qwen.yaml`
- `gemma` implemented in `packages/model_runner/voice_toolbench_model_runner/adapters/gemma.py` with `configs/models/gemma.yaml`

Required behavior:

- Each adapter must implement the common adapter contract.
- Each adapter must declare runtime and resource expectations.
- Each adapter must expose raw model output exactly as returned before parsing.
- Each adapter must not bypass canonical JSON parsing, schema validation, registry lookup, or artifact logging.
- Unit tests must use `MockModelAdapter`.
- Ordinary CI real-adapter checks are limited to import/config validation.
- Full real-model benchmarks are manual.
- GPU benchmarks use `workflow_dispatch` or self-hosted runners.

## Inference Profiles

```json
{
  "profile_id": "quantized_4bit",
  "precision_mode": "4bit",
  "model_family": "qwen",
  "memory_note": "Lower memory than base precision on supported runtimes.",
  "quality_note": "Compare against base profile on paired subset."
}
```

Required behavior:

- At least one quantized profile must be selectable by config.
- Required profile configs are `configs/inference/full_precision.yaml`, `configs/inference/quantized_8bit.yaml`, and `configs/inference/quantized_4bit.yaml`.
- `gguf_or_local_runtime` may be exposed when supported by the selected model.
- A quantized profile must declare supported model families.
- Comparisons must evaluate the same examples for base and quantized profiles.
