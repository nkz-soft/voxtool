# Feature Specification: Bilingual Voice Benchmark Demo

**Feature Branch**: `004-voice-benchmark-demo`

**Created**: 2026-06-06

**Status**: Draft

**Input**: User description: "Build a bilingual Russian/English voice assistant benchmark and demo system. The assistant must accept either text or audio input. It must decide whether a tool is required, generate a structured JSON tool invocation when needed, optionally execute the tool through a backend, and return a concise human-readable answer. The project must compare four pipelines: A. Text -> Model -> Tool Call; B. Audio -> Model/ASR -> Transcript; C. Audio -> Model -> Transcript + Tool Call in one pass; D. Audio -> ASR -> Transcript -> Model -> Tool Call. The main tool must be units.convert, not weather. It converts numeric values between simple units: meters, kilometers, centimeters, millimeters, grams, kilograms, pounds, ounces, Celsius, Fahrenheit. The system must generate a synthetic dataset: 200-300 text examples for units.convert; 10-20% no-tool examples; Russian and English examples; each example has expected needs_tool, expected tool_call, and expected final answer; each text example has a synthesized audio version. The benchmark must report Parsable Tool Invocation Rate, Tool decision accuracy, Tool-call exact match, Argument exact match, Precision, Recall, False Alarm Rate, WER for ASR, and Modality gap between text and audio. The system must include Tool schema, Prompt templates, JSON parser and validator, One retry/repair attempt for invalid JSON, Tool executor, Evaluation runner, Metrics report, Demo notebook, and optional FastAPI endpoint for demo execution. Success criteria: Pipeline A runs on at least 200 text examples; Pipeline B reports WER on an audio test subset; Pipelines C and D report tool-use metrics on audio; The final report identifies the best pipeline and explains failure cases."

## Clarifications

### Session 2026-06-06

- Q: What exact model output and tool schema should be required? -> A: Require every model tool-decision output to use one JSON envelope with `needs_tool`, `tool_call`, and `final_answer`; `tool_call` is null for no-tool cases or contains `tool: "units.convert"` and `arguments` with numeric `value`, `from_unit`, and `to_unit`; transcript-capable pipelines also include `transcript`.
- Q: How should invalid first-pass JSON and repaired JSON affect benchmark metrics? -> A: Parsable Tool Invocation Rate counts only first-pass valid JSON envelopes; repaired JSON is recorded in a separate repair-success field and may proceed to validation and execution, but does not count as first-pass parsable.
- Q: What dataset size, language balance, no-tool ratio, and split policy should be required? -> A: Generate 240 text examples: 120 Russian and 120 English; 15% no-tool overall and per language; use a deterministic 70/15/15 train/validation/test split stratified by language, tool/no-tool label, and unit family.
- Q: How should exact-match metrics treat partially correct tool calls? -> A: Official tool-call exact match requires correct `needs_tool`, tool name, value, source unit, and target unit; argument exact match reports per-field matches separately; partially correct calls count as incorrect for exact match but are categorized in failure analysis.
- Q: What counts as a no-tool false alarm, and what must the final report include? -> A: A no-tool false alarm is any example with expected `needs_tool=false` where output `needs_tool=true` or a non-null `tool_call`; final report must include dataset summary, per-pipeline metrics, language splits, tool/no-tool confusion matrix, WER, modality gap, best-pipeline rationale, and categorized failure cases.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Text Unit Conversion Baseline (Priority: P1)

A benchmark user runs text requests in Russian and English and receives a tool-use decision, a validated `units.convert` invocation when needed, optional execution output, and a concise final answer.

**Why this priority**: Text tool use is the baseline for comparing whether audio pipelines lose accuracy relative to equivalent written requests.

**Independent Test**: Run Pipeline A on the generated text dataset and verify expected tool decisions, exact tool-call matches, argument matches, optional conversion results, and final answers.

**Acceptance Scenarios**:

1. **Given** an English text request to convert 2 kilometers to meters, **When** Pipeline A processes the request, **Then** it marks that a tool is needed, emits a parsable `units.convert` invocation, validates the arguments, optionally executes the conversion, and returns a concise answer with 2000 meters.
2. **Given** a Russian text request that asks for a direct factual or conversational answer without conversion, **When** Pipeline A processes the request, **Then** it marks that no tool is needed, emits no tool invocation, and returns a concise direct answer.

---

### User Story 2 - Audio Transcription Baseline (Priority: P1)

A benchmark user runs audio versions of Russian and English examples and receives transcripts so speech recognition quality can be measured independently of tool calling.

**Why this priority**: Pipeline B establishes transcript quality and makes it possible to separate ASR errors from tool-decision and argument-extraction errors.

**Independent Test**: Run Pipeline B on an audio test subset whose reference transcripts are known and verify that WER is reported for Russian and English audio.

**Acceptance Scenarios**:

1. **Given** an English audio example with a known reference transcript, **When** Pipeline B processes it, **Then** the benchmark records the produced transcript and includes it in WER results.
2. **Given** a Russian audio example linked to a generated text example, **When** Pipeline B processes it, **Then** the transcript remains associated with the same semantic example and dataset split.

---

### User Story 3 - One-Pass Audio Tool Calling (Priority: P2)

A benchmark user runs audio requests through a single-pass audio-capable path and receives both a transcript and a tool-use result from the same pass.

**Why this priority**: Pipeline C measures whether one-pass audio processing can match or outperform cascaded ASR plus text tool calling.

**Independent Test**: Run Pipeline C on the audio dataset subset and verify transcript recording, parsable tool invocations, validation results, optional execution results, answers, and tool-use metrics.

**Acceptance Scenarios**:

1. **Given** an audio request to convert Fahrenheit to Celsius, **When** Pipeline C processes it, **Then** the output includes a transcript, a parsable `units.convert` invocation, validated arguments, optional tool result, and a concise final answer.
2. **Given** an audio example that does not require a tool, **When** Pipeline C processes it, **Then** the output records a transcript, marks no tool required, and returns a concise direct answer.

---

### User Story 4 - Cascaded Audio Tool Calling (Priority: P2)

A benchmark user runs audio requests through a transcript-first path and receives a tool-use result derived from the transcript.

**Why this priority**: Pipeline D provides the main comparison against one-pass audio tool calling and shows how transcription errors affect downstream tool use.

**Independent Test**: Run Pipeline D on the same audio examples as Pipeline C and compare transcript quality, tool-decision accuracy, exact matches, argument matches, and final answers under shared example IDs.

**Acceptance Scenarios**:

1. **Given** audio asking to convert pounds to kilograms, **When** Pipeline D processes it, **Then** the run records an ASR transcript, a validated `units.convert` invocation when needed, optional execution output, and a concise answer.
2. **Given** matching text and audio examples, **When** Pipelines A and D are evaluated, **Then** the report can compute the modality gap for equivalent semantics.

---

### User Story 5 - Benchmark Report and Demo Review (Priority: P3)

A reviewer opens the demo materials and final benchmark report to understand pipeline behavior, best-performing pipeline, and failure cases.

**Why this priority**: The benchmark is only useful if results can be inspected, reproduced, and explained by people evaluating voice assistant tool-use behavior.

**Independent Test**: Generate the metrics report and open the demo notebook to verify that it shows dataset samples, pipeline outputs, metric tables, best-pipeline selection, and failure-case summaries.

**Acceptance Scenarios**:

1. **Given** completed benchmark runs for Pipelines A-D, **When** the metrics report is generated, **Then** it reports all required metrics and identifies the best pipeline based on documented comparison rules.
2. **Given** representative Russian and English demo examples, **When** the demo notebook is run, **Then** it shows text and audio request handling, tool decisions, parsed JSON, optional execution, and final answers.

### Edge Cases

- Model output is not valid JSON on the first attempt.
- The single retry or repair attempt still produces invalid JSON.
- A model emits a supported tool name with missing, nonnumeric, or unsupported unit arguments.
- A model emits a tool other than `units.convert`.
- A no-tool example is incorrectly assigned a tool call.
- A tool-required example is incorrectly treated as no-tool.
- Audio transcription changes a number, language-specific unit word, decimal separator, or source/target direction.
- Russian and English examples express the same unit conversion with different word order or morphology.
- Temperature conversions require formulas rather than linear scale factors.
- Optional backend execution is disabled, unavailable, or returns an execution error after validation.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST accept text input for benchmark and demo requests.
- **FR-002**: The system MUST accept audio input for benchmark and demo requests.
- **FR-003**: The system MUST support Russian and English examples and outputs.
- **FR-004**: The system MUST decide whether each request requires a tool.
- **FR-005**: The system MUST emit structured JSON for tool-use decisions and tool invocations.
- **FR-006**: Every model tool-decision output MUST use one JSON envelope containing `needs_tool`, `tool_call`, and `final_answer`.
- **FR-007**: For no-tool outputs, `tool_call` MUST be null.
- **FR-008**: For tool-required outputs, `tool_call` MUST contain `tool: "units.convert"` and `arguments` with numeric `value`, `from_unit`, and `to_unit`.
- **FR-009**: Transcript-capable pipeline outputs MUST include `transcript` in the same JSON envelope.
- **FR-010**: The system MUST include a tool schema for `units.convert`.
- **FR-011**: The `units.convert` schema MUST support numeric values, source units, and target units.
- **FR-012**: The `units.convert` tool MUST support meters, kilometers, centimeters, millimeters, grams, kilograms, pounds, ounces, Celsius, and Fahrenheit.
- **FR-013**: The MVP MUST use `units.convert` as the main tool and MUST NOT require weather behavior.
- **FR-014**: The system MUST validate parsed JSON tool invocations before any execution.
- **FR-015**: The system MUST reject unsupported tool names, missing arguments, nonnumeric values, and unsupported units before execution.
- **FR-016**: The system MUST make one retry or repair attempt when the first model output is invalid JSON.
- **FR-017**: The system MUST preserve whether a tool invocation was valid on the first pass or only after repair.
- **FR-018**: Parsable Tool Invocation Rate MUST count only first-pass valid JSON envelopes.
- **FR-019**: Repaired JSON MUST be recorded with a separate repair-success indicator and MAY proceed to schema validation and optional execution.
- **FR-020**: The system MUST optionally execute validated tool invocations through a backend tool executor.
- **FR-021**: The system MUST return a concise human-readable answer for every processed request.
- **FR-022**: The system MUST compare Pipeline A: Text -> Model -> Tool Call.
- **FR-023**: The system MUST compare Pipeline B: Audio -> Model/ASR -> Transcript.
- **FR-024**: The system MUST compare Pipeline C: Audio -> Model -> Transcript + Tool Call in one pass.
- **FR-025**: The system MUST compare Pipeline D: Audio -> ASR -> Transcript -> Model -> Tool Call.
- **FR-026**: The system MUST generate a synthetic dataset containing exactly 240 text examples.
- **FR-027**: The generated dataset MUST contain exactly 120 Russian and 120 English text examples.
- **FR-028**: The generated dataset MUST include 15% no-tool examples overall and 15% no-tool examples within each language.
- **FR-029**: Every dataset example MUST include expected `needs_tool`, expected `tool_call`, and expected final answer.
- **FR-030**: Every text example MUST have a synthesized audio version linked to the same semantic example.
- **FR-031**: Every synthesized audio version MUST include metadata linking `audio_id`, `example_id`, reference transcript, audio path, synthesis settings, and generation method for reproducibility.
- **FR-032**: Text and audio examples MUST share stable IDs so modality gap can be measured on equivalent requests.
- **FR-033**: Dataset releases MUST be versioned and reproducible with deterministic 70/15/15 train, validation, and test splits.
- **FR-034**: Dataset splits MUST be stratified by language, tool/no-tool label, and unit family.
- **FR-035**: The system MUST include prompt templates for text tool calling, audio transcription, one-pass audio tool calling, and cascaded audio tool calling.
- **FR-036**: The system MUST include an evaluation runner for Pipelines A-D.
- **FR-037**: The system MUST report Parsable Tool Invocation Rate.
- **FR-038**: The system MUST report tool decision accuracy.
- **FR-039**: Official tool-call exact match MUST require correct `needs_tool`, tool name, numeric value, source unit, and target unit.
- **FR-040**: Partially correct tool calls MUST count as incorrect for official tool-call exact match.
- **FR-041**: Argument exact match MUST include separate per-field match rates for numeric value, source unit, and target unit.
- **FR-042**: The system MUST categorize partially correct tool calls in failure analysis.
- **FR-043**: The system MUST report precision, recall, and false alarm rate for tool-use decisions.
- **FR-044**: A no-tool false alarm MUST be counted whenever an example with expected `needs_tool=false` outputs `needs_tool=true` or a non-null `tool_call`.
- **FR-045**: The system MUST report WER for ASR/transcript outputs on an audio test subset.
- **FR-046**: The system MUST report modality gap between text and audio results.
- **FR-047**: The system MUST record inputs, raw outputs, parsed outputs, validation errors, repair attempts, optional execution results, final answers, and metrics for benchmark runs.
- **FR-048**: The metrics report MUST include dataset summary, per-pipeline metrics, language-specific metric splits, tool/no-tool confusion matrix, WER, modality gap, best-pipeline rationale, and categorized failure cases.
- **FR-049**: The system MUST include a metrics report that identifies the best pipeline and explains failure cases.
- **FR-050**: The system MUST include a demo notebook that demonstrates text input, audio input, JSON parsing and validation, optional tool execution, and final answers.
- **FR-051**: The system SHOULD include an optional demo execution endpoint for sending requests and receiving parsed outputs, execution results, and answers.

### Key Entities *(include if feature involves data)*

- **Benchmark Example**: A generated semantic request with language, reference text, expected tool decision, expected tool invocation when applicable, expected answer, split, and stable ID.
- **Audio Example**: A synthesized audio version of a benchmark example linked to the same stable ID, language, reference transcript, and split.
- **Tool Invocation**: A structured request naming `units.convert` with numeric value, source unit, and target unit.
- **Model Output Envelope**: A structured JSON object containing `needs_tool`, `tool_call`, and `final_answer`, plus `transcript` for transcript-capable pipelines.
- **Pipeline Output**: The recorded result from one pipeline for one example, including raw output, parsed JSON envelope when available, first-pass parsability, repair-success status, validation status, transcript when available, optional execution result, final answer, and error details.
- **Metric Result**: Aggregated measurements for one pipeline and dataset subset, including tool-use metrics, WER, and modality-gap comparisons.
- **Tool Decision Confusion Matrix**: A count of true positives, false positives, true negatives, and false negatives based on expected and observed `needs_tool` behavior, where false positives include no-tool false alarms.
- **Failure Case**: A recorded example where the output differs from expectation, categorized by JSON parsing, schema validation, tool decision, tool name, numeric value, source unit, target unit, transcript, execution, or answer error.
- **Demo Request**: A text or audio request submitted through the notebook or optional demo endpoint with returned decision, parsed output, execution result, and answer.

### Benchmark and Dataset Requirements *(mandatory for benchmark changes)*

- **Dataset Version**: Each synthetic dataset release has a stable version identifier and records generation settings.
- **Split Strategy**: Dataset examples are assigned to deterministic 70/15/15 train, validation, and test splits stratified by language, tool/no-tool label, and unit family.
- **Languages**: Russian and English are balanced at 120 text examples each; each language includes 15% no-tool examples.
- **Modalities**: Text and synthesized audio examples must remain aligned through shared semantic IDs.
- **Allowed Tools**: `units.convert` is the only required MVP tool; weather is out of scope.
- **Artifact Logging**: Each run records inputs, raw outputs, parsed outputs, validation errors, repair attempts, optional execution results, answers, and metrics.
- **Failure Handling**: Invalid first-pass JSON, failed repair, schema validation errors, unsupported tool calls, incorrect tool decisions, partially correct arguments, transcript errors, and optional execution failures are recorded explicitly; repaired JSON is distinguishable from first-pass valid JSON.
- **CI Evidence**: Normal validation must be able to run a bounded smoke benchmark without relying on large generated artifacts or unavailable external resources.
- **Full Benchmark Trigger**: Full audio/model benchmark runs may be performed separately from bounded validation runs when they require heavier resources.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Pipeline A runs on at least 200 generated text examples with recorded outputs and all required tool-use metrics.
- **SC-002**: The generated dataset contains exactly 240 text examples, with 120 Russian and 120 English examples, and 15% no-tool examples overall and per language.
- **SC-003**: 100% of generated text examples have expected `needs_tool`, expected `tool_call`, expected final answer, and a linked synthesized audio version.
- **SC-004**: Pipeline B reports WER on an audio test subset that includes Russian and English examples.
- **SC-005**: Pipelines C and D report Parsable Tool Invocation Rate, tool decision accuracy, tool-call exact match, argument exact match, precision, recall, and false alarm rate on audio examples.
- **SC-006**: The benchmark report includes modality-gap results comparing text and audio outcomes for shared semantic IDs.
- **SC-007**: The benchmark report includes dataset summary, per-pipeline metrics, language-specific metric splits, tool/no-tool confusion matrix, WER, modality gap, best-pipeline rationale, and categorized failure cases.
- **SC-008**: Invalid first-pass JSON receives no more than one retry or repair attempt, and the report distinguishes first-pass valid JSON from repaired JSON.
- **SC-009**: The demo notebook shows at least one Russian and one English example for text input, audio transcription, audio tool calling, optional execution, and final answer display.

## Assumptions

- The benchmark's primary audience is developers and evaluators comparing voice assistant tool-use behavior, not end users of a production assistant.
- No-tool examples are simple direct-answer or conversational requests that should not invoke `units.convert`.
- Expected final answers may use a documented rounding tolerance for converted numeric values.
- Synthesized audio quality is sufficient for repeatable benchmarking, while full natural-speech robustness can be evaluated later.
- Optional backend execution can be disabled for dry-run evaluation, but parsing and validation still run.
- The optional demo endpoint is secondary to the benchmark runner, metrics report, and demo notebook.
