# Feature Specification: Advanced Benchmark Phases

**Feature Branch**: `003-advanced-benchmark-phases`

**Created**: 2026-06-12

**Status**: Draft

**Input**: User description: "Extend Voice Assistant ToolBench with three advanced implementation phases: real model adapters and Colab demo; LoRA fine-tuning and Russian dataset; speech output, multiple tools, and quantization."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run Real-Model Colab Demo (Priority: P1)

As a benchmark researcher, I want to run a hosted notebook demonstration with a real model family selected from Voxtral, Qwen, or Gemma so that I can see end-to-end tool-call behavior on small bilingual examples without setting up the full project locally.

**Why this priority**: This is the first externally demonstrable step beyond deterministic mocks and proves that the benchmark can exercise real model output while keeping ordinary project validation lightweight.

**Independent Test**: Can be tested by opening the demo, selecting at least one supported real adapter, running text examples through Pipeline A, and confirming that each example shows raw output, parsed JSON, validation status, tool execution result, final answer, and a metrics summary.

**Acceptance Scenarios**:

1. **Given** a small sample dataset and a supported runtime, **When** the user selects a real adapter and runs Pipeline A, **Then** the demo shows raw model output, parsed tool-call JSON, validation result, execution result, final answer, and aggregate metrics for each processed example.
2. **Given** an audio-capable runtime and a compatible selected adapter, **When** the user enables audio execution, **Then** the demo runs the appropriate audio pipeline and records transcript, tool-call, validation, execution, answer, and metrics outputs.
3. **Given** an ordinary continuous-integration environment without large model downloads or GPU access, **When** validation runs, **Then** the real-adapter surfaces are covered by mocks or bounded smoke tests without requiring heavyweight model execution.

---

### User Story 2 - Improve Russian Tool Calling with Fine-Tuning (Priority: P2)

As a model evaluator, I want a Russian-focused instruction-tuning workflow and before/after comparison so that I can measure whether adaptation improves structured tool-call generation on Russian requests.

**Why this priority**: Russian accuracy is central to the benchmark. Fine-tuning support is valuable only when it produces reproducible datasets, splits, and reports that can distinguish improvement from chance.

**Independent Test**: Can be tested by generating or importing a Russian instruction-tuning dataset, verifying deterministic train/validation/test splits, running a base-versus-adapted evaluation on a bounded subset, and confirming Russian-only metrics and deltas are reported.

**Acceptance Scenarios**:

1. **Given** Russian examples for conversions, no-tool requests, ambiguous wording, and speech-style requests, **When** the dataset workflow runs, **Then** it produces versioned instruction-tuning records with deterministic train, validation, and test membership.
2. **Given** a base model result and an adapted model result for the same Russian evaluation subset, **When** the comparison report is generated, **Then** it includes parsability, tool-decision accuracy, exact tool-call matching, exact argument matching, false-alarm rate, Russian-only metrics, and before/after deltas.
3. **Given** future multi-tool examples are available, **When** the Russian dataset is extended, **Then** second-tool examples can be included without breaking existing conversion, no-tool, ambiguity, or speech-style categories.

---

### User Story 3 - Evaluate Assistant Mode with Speech, Multiple Tools, and Quantization (Priority: P3)

As a demo user and benchmark maintainer, I want final answers to optionally produce speech output, tool calls to route across a small supported tool set, and inference profiles to include quantized operation so that the system can be evaluated as a practical assistant beyond benchmark-only text outputs.

**Why this priority**: These capabilities broaden the benchmark surface after real adapters and Russian tuning are in place, while preserving strict validation and reproducible metric reporting.

**Independent Test**: Can be tested by running a small evaluation that includes each supported tool, optional speech output, and a base-versus-quantized profile comparison, then checking per-tool metrics, saved speech paths, and quantization trade-off notes.

**Acceptance Scenarios**:

1. **Given** a validated final text answer and speech output enabled, **When** the example completes, **Then** an audio file is generated and the evaluation or demo output records its path.
2. **Given** predicted tool calls for unit conversion, Russian stress placement, and simple arithmetic, **When** the system validates and executes them, **Then** each call is routed to the correct supported tool and per-tool metrics are reported.
3. **Given** a quantized inference profile and a comparable base-precision profile, **When** the small evaluation subset runs, **Then** the report compares quality metrics and records memory and usability trade-offs for the selected profile.

### Edge Cases

- A selected real adapter is unavailable in the current runtime or lacks the capability required by the requested pipeline.
- A model emits malformed JSON, an unsupported tool name, missing arguments, wrong argument types, or a no-tool answer when a tool is expected.
- Audio examples are requested in an environment that lacks compatible runtime support.
- Speech output is enabled but audio generation fails after the final answer is produced.
- Quantized operation is selected for a model family or runtime that cannot support the requested profile.
- Russian examples contain ambiguous wording where both a tool call and a no-tool response may appear plausible; labels must make the expected behavior explicit.
- Multi-tool evaluation includes an example for a tool that is not registered as supported.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support real-model execution surfaces for Voxtral, Qwen, and Gemma model families through a common adapter contract usable by text-to-tool and audio-to-tool benchmark pipelines.
- **FR-002**: System MUST allow Pipeline A to process text examples with a selected real adapter and produce raw output, parsed JSON, validation result, optional tool execution result, final answer, and per-example metrics.
- **FR-003**: System MUST allow Pipeline C to process audio examples directly with an audio-capable selected adapter and produce transcript, tool-call, validation, execution, answer, and metrics artifacts when runtime support is available.
- **FR-004**: System MUST allow Pipeline D to process audio examples through transcription followed by model tool-call generation and produce transcript, tool-call, validation, execution, answer, and metrics artifacts.
- **FR-005**: System MUST provide a hosted-notebook demo flow that installs required runtime dependencies, loads a bounded sample dataset, selects a model adapter, runs text examples, optionally runs audio examples, displays per-example artifacts, and builds a small metrics table.
- **FR-006**: System MUST keep ordinary continuous integration free of large model downloads, GPU requirements, and mandatory remote model execution.
- **FR-007**: System MUST validate real-adapter behavior in ordinary CI through mocks or bounded smoke tests that verify contract compatibility and pipeline integration.
- **FR-008**: System MUST create or import instruction-tuning records for structured tool-call generation, including prompts, expected model decisions, expected JSON envelopes, language labels, split labels, and evaluation labels.
- **FR-009**: System MUST provide a Russian dataset slice that includes `units.convert` requests, no-tool requests, ambiguous wording requests, and speech-style requests.
- **FR-010**: System MUST support deterministic train, validation, and test splits for fine-tuning datasets and preserve version metadata for generated or imported data.
- **FR-011**: System MUST define a trainable adaptation configuration and a reproducible training entrypoint or notebook for supervised adaptation of structured tool-call generation.
- **FR-012**: System MUST evaluate base and adapted model outputs on the same Russian evaluation subset and report before/after deltas.
- **FR-013**: System MUST report `parsable_rate`, `tool_decision_accuracy`, `tool_call_exact_match`, `argument_exact_match`, `false_alarm_rate`, Russian-only metrics, and before/after deltas for fine-tuning evaluation.
- **FR-014**: System MUST optionally generate speech audio from a final text answer and record the generated audio path in demo and evaluation outputs.
- **FR-015**: System MUST keep speech-output generation optional and disabled in ordinary CI unless a bounded mock or fixture-based validation is used.
- **FR-016**: System MUST support multiple tools through an explicit supported-tool registry, strict schema validation, and routing of each validated predicted tool call to the matching executor.
- **FR-017**: System MUST include `units.convert`, `text.stress_ru`, and `calculator.simple` in the supported tool set for this phase.
- **FR-018**: System MUST report per-tool metrics for supported tools, including correct tool decision, exact tool-call match, exact argument match, validation failure rate, execution success rate, and false-alarm rate where applicable.
- **FR-019**: System MUST reject unsupported tool calls and include the failure in per-example artifacts and aggregate metrics.
- **FR-020**: System MUST provide at least one selectable quantized inference profile for supported real-model evaluation.
- **FR-021**: System MUST compare base-precision and quantized inference on a bounded evaluation subset and report quality metrics alongside memory and usability trade-offs.
- **FR-022**: System MUST define benchmark metrics before declaring the feature successful.
- **FR-023**: System MUST validate tool calls against schema before execution.
- **FR-024**: System MUST log invalid JSON as a failure with raw model output and validation details, while keeping repaired output distinguishable from first-pass valid JSON.
- **FR-025**: System MUST version datasets and produce deterministic train/validation/test splits.
- **FR-026**: System MUST support Russian and English requests where existing benchmark coverage is affected, and MUST provide dedicated Russian metrics for the Russian dataset and adaptation workflow.
- **FR-027**: System MUST save experiment inputs, raw outputs, parsed outputs, validation errors, repair attempts, execution results, final answers, speech-output paths when enabled, and metrics.
- **FR-028**: System MUST NOT require weather behavior for this feature.
- **FR-029**: System MUST run PR CI with lint, formatting check, typecheck, tests, and a deterministic smoke benchmark.
- **FR-030**: System MUST run full real-model, audio, fine-tuning, speech, or quantized experiments manually or on suitable non-ordinary-CI runners when heavyweight resources are required.
- **FR-031**: System MUST NOT commit large generated datasets, audio, model outputs, checkpoints, or benchmark reports to Git.
- **FR-032**: Pull requests MUST link to a spec task and include validation evidence for CI, smoke benchmark output, and any manual heavyweight run artifacts relevant to the change.
- **FR-033**: Public package interfaces, command surfaces, notebook helpers, and benchmark-critical behaviors introduced by this feature MUST include concise descriptions of purpose, important inputs or outputs, and failure behavior when not obvious.

### Key Entities

- **Model Adapter**: A selectable model execution capability for a supported model family, with declared text, audio, quantization, and resource capabilities.
- **Demo Run**: A small interactive execution session containing selected adapter, selected pipelines, input examples, raw outputs, parsed outputs, validation results, execution results, final answers, speech paths when enabled, and metrics table.
- **Instruction-Tuning Record**: A labeled training or evaluation item containing request text, language, expected tool decision, expected JSON envelope, expected final answer behavior, category labels, and split membership.
- **Russian Dataset Slice**: The Russian-language subset used for training and evaluation, covering conversion, no-tool, ambiguity, speech-style, and future multi-tool categories.
- **Adaptation Run**: A base or adapted model comparison run that records dataset version, split, selected model family, training configuration reference, outputs, metrics, and before/after deltas.
- **Tool Registry Entry**: A supported tool definition with name, schema, executor routing, validation behavior, and reporting labels.
- **Speech Output Artifact**: Generated answer audio with path, input text answer, generation status, and failure details when generation is requested.
- **Inference Profile**: A selectable model-loading or execution profile with precision mode, resource expectations, quality metrics, and trade-off notes.

### Benchmark and Dataset Requirements *(mandatory for benchmark changes)*

- **Dataset Version**: This feature MUST introduce a new dataset version or compatible extension identifier for advanced real-model, Russian adaptation, multi-tool, speech, and quantization evaluations.
- **Split Strategy**: Fine-tuning and evaluation datasets MUST use deterministic train/validation/test splits, preserving language, tool/no-tool label, and category balance where practical.
- **Languages**: Russian and English remain supported for benchmark compatibility; Russian MUST have dedicated metrics for dataset and adaptation workflows.
- **Modalities**: Text examples MUST support Pipeline A; audio examples MUST support Pipeline C and Pipeline D when the selected runtime and adapter capability allow it. Text and audio artifacts for the same semantic example MUST remain traceable.
- **Allowed Tools**: `units.convert`, `text.stress_ru`, and `calculator.simple` are supported. Weather remains out of scope.
- **Artifact Logging**: Every run MUST save inputs, raw model outputs, parsed outputs, validation errors, repair attempts, execution results, final answers, speech-output paths when enabled, per-example metrics, aggregate metrics, and relevant run configuration references.
- **Failure Handling**: Invalid JSON, schema validation errors, unsupported tool calls, unavailable adapter capabilities, speech-generation failures, and unsupported quantized profiles MUST be explicit failures or skipped-capability outcomes in artifacts and reports.
- **CI Evidence**: Ordinary CI MUST include lint, formatting check, typecheck, tests, and a deterministic smoke benchmark using mocks or bounded fixtures.
- **Full Benchmark Trigger**: Real-model, full audio, fine-tuning, speech-generation, and quantized-profile comparisons that need heavyweight resources MUST be manual or run on suitable non-ordinary-CI runners.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A demo user can run Pipeline A end-to-end with at least one real supported model family on a bounded sample dataset and see raw output, parsed JSON, validation, execution, final answer, and metrics for at least 5 examples.
- **SC-002**: Ordinary CI completes without downloading large models or requiring GPU resources while still validating adapter compatibility through mocks or bounded smoke tests.
- **SC-003**: The Russian instruction-tuning workflow produces train, validation, and test splits with all required Russian categories represented and version metadata recorded.
- **SC-004**: The base-versus-adapted Russian evaluation report includes all required metrics and before/after deltas for at least one bounded Russian evaluation subset.
- **SC-005**: Speech-output demo mode generates an audio file for at least one final answer and records the path in the run output.
- **SC-006**: Multi-tool evaluation reports per-tool metrics for `units.convert`, `text.stress_ru`, and `calculator.simple` on a bounded evaluation subset containing at least one valid example for each tool.
- **SC-007**: Quantized inference can be selected by configuration and produces a comparison report against base precision on a bounded subset, including quality metrics and memory or usability trade-off notes.
- **SC-008**: Invalid JSON, unsupported tools, schema failures, unavailable runtime capabilities, and disabled heavyweight features are represented clearly in artifacts and aggregate metrics.

## Assumptions

- The existing benchmark pipelines, JSON envelope rules, validation behavior, and artifact conventions remain the baseline for these phases.
- Hosted notebook execution is intended for demonstration and manual experimentation, not as a substitute for ordinary CI.
- Large model files, checkpoints, generated audio, full benchmark outputs, and training artifacts remain outside version control.
- The first real-model demo requirement can be satisfied by any one of the supported model families when runtime constraints prevent all families from running in the same environment.
- Speech output is evaluated as an optional assistant-mode artifact and does not change the correctness of tool-call metrics unless speech generation itself is under test.
- Multi-tool support remains limited to the explicitly supported tool set until a later specification expands it.
