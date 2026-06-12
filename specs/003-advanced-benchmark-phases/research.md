# Research: Advanced Benchmark Phases

## Real Model Adapter Boundary

**Decision**: Extend the existing `ModelAdapter` boundary with `generate_text(prompt, config) -> ModelResponse` and declared capability flags: `supports_audio_input`, `supports_text_input`, `supports_lora`, and `supports_quantization`. Implement `VoxtralAdapter`, `QwenAdapter`, and `GemmaAdapter` in `packages/model_runner/voice_toolbench_model_runner/adapters/voxtral.py`, `qwen.py`, and `gemma.py`, backed by `configs/models/voxtral.yaml`, `qwen.yaml`, and `gemma.yaml`. CI uses `MockModelAdapter`, import tests, config tests, and bounded smoke fixtures only.

**Rationale**: Pipelines A, C, and D need to choose adapters by capability without hard-coding model families. Capability declarations make unsupported Colab/runtime combinations explicit skipped-capability outcomes instead of ambiguous failures.

**Alternatives considered**: Pipeline-specific model adapters were rejected because they duplicate orchestration and artifact logic. Downloading real models in CI was rejected because ordinary validation must remain GPU-free and lightweight.

## Colab Demo Scope

**Decision**: Provide one Colab-ready notebook at `apps/notebook/colab_demo.ipynb` that installs optional demo dependencies, clones or loads the repository, loads a small fixture or generated subset, selects a supported adapter from config, runs text examples by default, optionally uploads an audio file when capabilities allow it, runs inference, validates the JSON tool call, executes the tool, shows the final answer, and displays metrics.

**Rationale**: A single notebook is enough to prove real-model execution while keeping project CI and local smoke validation independent from hosted runtime constraints.

**Alternatives considered**: A full web UI was rejected as outside the benchmark scope. Requiring all three real model families in one run was rejected because Colab runtimes vary in memory, GPU, and model availability.

## LoRA/SFT Workflow

**Decision**: Use JSONL instruction-tuning records built by `packages/finetuning/voice_toolbench_finetuning/dataset.py` and `scripts/build_sft_dataset.py`, with deterministic train/validation/test splits, LoRA config models in `lora_config.py`, training in `train.py` and `scripts/train_lora.py`, and evaluation in `evaluate.py` and `scripts/evaluate_lora.py`. Records contain `instruction`, `input`, `expected_output_json`, `locale`, `tool_name`, `split`, `source`, and `difficulty`.

**Rationale**: JSONL matches existing dataset and artifact conventions, keeps examples inspectable, and lets the same evaluation metrics compare base and adapted outputs.

**Alternatives considered**: Free-form notebook-only data preparation was rejected because it is not reproducible. Committing checkpoints was rejected by Git hygiene and artifact-size constraints.

## Russian Dataset Categories

**Decision**: Configure Russian datasets through `configs/datasets/ru_units_convert.yaml` and `configs/datasets/ru_toolbench.yaml`, with category labels for `units_convert`, `no_tool`, `ambiguous_wording`, `speech_style`, and optional future multi-tool categories when registry support is present.

**Rationale**: The fine-tuning success criteria require Russian-only metrics and specific behavioral slices. Category labels allow targeted failure analysis without changing the canonical JSON envelope.

**Alternatives considered**: A single undifferentiated Russian split was rejected because it would hide ambiguity, no-tool false alarms, and speech-style regressions.

## Multi-Tool Validation

**Decision**: Keep the single `ToolCall` shape with a free tool name resolved through `ToolRegistry`, and make the execution boundary explicit as `ToolDefinition`, `ToolRegistry`, `ToolExecutor`, and `ToolSchemaValidator`. Add provider schemas, deterministic executors, examples, tests, and metric grouping for `text.stress_ru` and `calculator.simple` alongside `units.convert`.

**Rationale**: The existing registry design already supports strict validation and executor routing. Adding tools through providers avoids pipeline-specific dispatch and preserves prompt construction from manifests.

**Alternatives considered**: Adding a separate model-output schema per tool was rejected because it would fragment parsing. Allowing arbitrary tools was rejected because unsupported tool calls must be benchmark failures.

## Speech Output

**Decision**: Add `packages/speech_output/voice_toolbench_speech_output/` with a `SpeechSynthesizer` interface, `PiperSpeechSynthesizer` or `EdgeTtsSpeechSynthesizer`, an audio manifest writer, and demo integration. Treat answer speech as an optional post-answer artifact with `speech_output_path`, generation status, provider/profile metadata, and failure details. Speech generation is disabled in ordinary CI except for mock or tiny fixture validation.

**Rationale**: Speech output is assistant-mode behavior, not part of tool-call correctness. Recording it as an optional artifact preserves traceability without contaminating existing tool metrics.

**Alternatives considered**: Making speech mandatory for all runs was rejected because CI and many model-evaluation paths do not need audio generation. Storing generated speech in Git was rejected.

## Quantized Inference Profiles

**Decision**: Represent quantization as selectable inference profiles from `configs/inference/full_precision.yaml`, `quantized_8bit.yaml`, and `quantized_4bit.yaml`, with optional `gguf_or_local_runtime` support when selected models support it. Reports include memory notes when available, latency per example when measured, parsable rate, exact tool-call match, and quality delta against the non-quantized baseline.

**Rationale**: Profile-based selection lets adapters expose supported quantized modes while reports compare quality and resource trade-offs consistently.

**Alternatives considered**: Hard-coding one quantization implementation into every adapter was rejected because model families differ. Treating quantization as only documentation was rejected because the feature requires selectable config and measured comparison.

## CI Boundary

**Decision**: Ordinary CI validates contracts, schemas, registry behavior, dataset splitting, metrics, pipeline orchestration, adapter capability handling, and mock speech/quantization paths only. Heavyweight runs are manual or suitable-runner workflows.

**Rationale**: This preserves reliable PR feedback and satisfies the requirement that normal GitHub CI does not download large models or require GPU.

**Alternatives considered**: Skipping real-adapter tests entirely was rejected because the adapter contract can regress. Running full real-model smoke tests in every PR was rejected due to cost and runtime instability.
