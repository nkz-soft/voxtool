# Feature Specification: Multilingual Voice Benchmark Demo

**Feature Branch**: `001-voice-benchmark-planning`

**Created**: 2026-06-06

**Status**: Draft

**Input**: User description: "Build a multilingual voice assistant benchmark and demo system. The assistant must accept either text or audio input. It must decide whether a tool is required, generate a structured JSON tool invocation when needed, optionally execute the tool through a backend, and return a concise human-readable answer. The project must compare four pipelines: A. Text -> Model -> Tool Call; B. Audio -> Model/ASR -> Transcript; C. Audio -> Model -> Transcript + Tool Call in one pass; D. Audio -> ASR -> Transcript -> Model -> Tool Call. The main tool must be units.convert. It converts numeric values between simple units: meters, kilometers, centimeters, millimeters, grams, kilograms, pounds, ounces, Celsius, Fahrenheit. The repository must include apps/, packages/, configs/, data/, reports/, scripts/, specs/, tests/, .github/. CI/CD must be implemented with GitHub Actions: ci.yml for lint, format check, typecheck, tests, and coverage artifact; benchmark-smoke.yml for deterministic benchmark using MockModelAdapter; report.yml for manually triggered full benchmark report generation; release.yml for tag-based release with report artifacts. Normal PR CI must not require GPU, real model downloads, paid APIs, or large audio generation. Generated datasets, audio files, benchmark outputs, model checkpoints, and reports must not be committed to Git, except small test fixtures and .gitkeep files. Pull requests must use a template and link to Speckit task IDs. Experiment issues must capture hypothesis, pipeline, setup, metrics, and result."

## Clarifications

### Session 2026-06-06

- Q: What exact repository structure should be required? -> A: Top-level required folders plus fixed package areas: `packages/dataset_builder`, `packages/tts_synth`, `packages/model_runner`, `packages/pipeline_runner`, `packages/tool_schema`, `packages/metrics`, `packages/report_builder`, with `apps/api`, `apps/cli`, and `apps/notebook`.
- Q: What artifact retention policy should workflow outputs use? -> A: PR coverage and smoke benchmark artifacts retained for 14 days; manual full benchmark and release report artifacts retained for 90 days.
- Q: Which workflows or operations must be manual-only? -> A: Full audio/model benchmarks, real model runs, paid API runs, large audio generation, report generation, and release publishing.
- Q: Which GitHub issue types are required? -> A: Feature Task, Benchmark Experiment, Bug, and Documentation/Process.
- Q: What must the smoke benchmark verify? -> A: All four pipelines using MockModelAdapter, English and Russian, tool-required and no-tool examples, invalid JSON/schema cases, and metrics/artifacts.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Text Conversion Request (Priority: P1)

A benchmark user submits a Russian or English text request that requires a unit conversion and receives a concise answer backed by a valid structured tool invocation.

**Why this priority**: Text tool calling is the baseline pipeline and establishes the expected behavior for schema validation, JSON output, tool execution, and answer generation.

**Independent Test**: Can be tested by submitting representative Russian and English text conversion requests and verifying that Pipeline A produces valid JSON, a validated `units.convert` call, and the expected concise answer.

**Acceptance Scenarios**:

1. **Given** an English request to convert 2 kilometers to meters, **When** the user submits text input, **Then** Pipeline A emits a valid JSON tool invocation for `units.convert`, validates it, executes it when backend execution is enabled, and returns a concise answer with 2000 meters.
2. **Given** a Russian request to convert 500 grams to kilograms, **When** the user submits text input, **Then** Pipeline A emits a valid JSON tool invocation for `units.convert`, validates it, executes it when backend execution is enabled, and returns a concise answer with 0.5 kilograms.

---

### User Story 2 - Audio Transcript Baseline (Priority: P1)

A benchmark user submits audio in Russian or English and receives a transcript so audio understanding can be compared against text examples.

**Why this priority**: Transcript quality is required to interpret the audio-only benchmark paths and to diagnose modality gaps between text and audio inputs.

**Independent Test**: Can be tested by submitting fixed audio fixtures for semantic examples already present in the text dataset and verifying that Pipeline B returns transcripts tied to the same dataset items.

**Acceptance Scenarios**:

1. **Given** an English audio request with no required tool call, **When** Pipeline B processes the audio, **Then** it returns a transcript and records the transcript output for evaluation.
2. **Given** a Russian audio request that matches a text semantic example, **When** Pipeline B processes the audio, **Then** the transcript is associated with the same dataset item and split as the text example.

---

### User Story 3 - One-Pass Audio Tool Calling (Priority: P2)

A benchmark user submits audio requiring unit conversion and receives both a transcript and a validated tool call from a single audio model pass.

**Why this priority**: Pipeline C evaluates whether a model can jointly transcribe and decide tool use from audio without an intermediate ASR stage.

**Independent Test**: Can be tested by running Pipeline C on fixed Russian and English audio examples and verifying transcript output, valid JSON, schema validation, optional tool execution, and concise answers.

**Acceptance Scenarios**:

1. **Given** audio requesting Fahrenheit to Celsius conversion, **When** Pipeline C processes it, **Then** the run records a transcript, a valid `units.convert` JSON invocation, validation result, optional backend execution result, and a concise answer.
2. **Given** audio that does not require a tool, **When** Pipeline C processes it, **Then** the run records a transcript, marks tool use as not required, and returns a concise direct answer.

---

### User Story 4 - Cascaded Audio Tool Calling (Priority: P2)

A benchmark user submits audio requiring unit conversion and receives a validated tool call after audio is transcribed and passed through the text tool-calling path.

**Why this priority**: Pipeline D is the main comparison point for determining whether one-pass audio tool calling outperforms or underperforms an ASR plus text-model cascade.

**Independent Test**: Can be tested by running Pipeline D on the same audio examples used by Pipeline C and comparing transcript, tool-call, answer, and metric outputs for the same dataset items.

**Acceptance Scenarios**:

1. **Given** an audio request to convert pounds to kilograms, **When** Pipeline D processes it, **Then** the run records the ASR transcript, valid `units.convert` JSON invocation, validation result, optional backend execution result, and concise answer.
2. **Given** the same semantic example in text and audio forms, **When** Pipelines A and D are evaluated, **Then** their outputs can be compared under shared dataset IDs and deterministic splits.

---

### User Story 5 - Pull Request Validation (Priority: P3)

A contributor opens a pull request and can demonstrate that benchmark, CI, artifact, and traceability requirements are satisfied without relying on expensive or GPU-dependent work.

**Why this priority**: The repository must remain maintainable and verifiable as benchmark pipelines, datasets, and reports evolve.

**Independent Test**: Can be tested by opening a pull request that links Speckit task IDs, runs normal CI, uploads deterministic smoke benchmark and coverage artifacts, and includes validation evidence in the PR template.

**Acceptance Scenarios**:

1. **Given** a normal pull request, **When** CI runs, **Then** lint, formatting check, typecheck, tests, and deterministic smoke benchmark complete without GPU, real model downloads, paid APIs, or large audio generation.
2. **Given** an experiment issue, **When** the issue is created, **Then** it captures hypothesis, pipeline, setup, metrics, and result.

### Edge Cases

- Invalid model output that is not machine-readable JSON is recorded as a failure with raw output and validation details.
- A JSON tool invocation with an unsupported tool name is rejected before execution.
- A JSON `units.convert` invocation with missing, nonnumeric, or unsupported unit arguments is rejected before execution.
- A request that does not need a tool returns a direct concise answer and records that no tool was required.
- Audio examples with poor transcription quality remain tied to the same dataset item so transcript errors can be separated from tool-call errors.
- Normal pull request CI never depends on large generated artifacts, GPU access, paid APIs, real model downloads, or bulk audio generation.
- Generated datasets, audio files, benchmark outputs, model checkpoints, and reports are excluded from Git except small test fixtures and `.gitkeep` files.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST accept text input for benchmark and demo requests.
- **FR-002**: The system MUST accept audio input for benchmark and demo requests.
- **FR-003**: The system MUST decide whether each request requires a tool call.
- **FR-004**: The system MUST emit machine-readable JSON for model outputs that include tool-call decisions.
- **FR-005**: The system MUST treat invalid JSON as a failed model output and log the raw output and validation details.
- **FR-006**: The system MUST validate every tool invocation against schema before execution.
- **FR-007**: The system MUST optionally execute validated tool calls through a backend.
- **FR-008**: The system MUST return a concise human-readable answer for each processed request.
- **FR-009**: The system MUST compare Pipeline A: text input to model to tool call.
- **FR-010**: The system MUST compare Pipeline B: audio input to model or ASR to transcript.
- **FR-011**: The system MUST compare Pipeline C: audio input to transcript and tool call in one pass.
- **FR-012**: The system MUST compare Pipeline D: audio input to ASR transcript to model to tool call.
- **FR-013**: The system MUST support `units.convert` as the main tool.
- **FR-014**: The `units.convert` tool MUST support conversions among meters, kilometers, centimeters, millimeters, grams, kilograms, pounds, ounces, Celsius, and Fahrenheit.
- **FR-015**: The MVP MUST NOT require weather behavior in datasets, prompts, schemas, pipelines, tests, or reports.
- **FR-016**: The system MUST support Russian and English benchmark requests.
- **FR-017**: Text and audio evaluations MUST use the same semantic examples to measure modality gap.
- **FR-018**: All datasets MUST be versioned and use deterministic train, validation, and test splits.
- **FR-019**: Every experiment MUST save inputs, raw model outputs, parsed outputs, validation errors, and metrics.
- **FR-020**: The repository MUST include `apps/`, `packages/`, `configs/`, `data/`, `reports/`, `scripts/`, `specs/`, `tests/`, and `.github/`.
- **FR-021**: The repository MUST keep dataset generation, TTS, model runner, pipeline runner, tool schema, metrics, and report generation in fixed package areas: `packages/dataset_builder`, `packages/tts_synth`, `packages/model_runner`, `packages/pipeline_runner`, `packages/tool_schema`, `packages/metrics`, and `packages/report_builder`.
- **FR-022**: CI MUST include a normal pull request workflow for lint, formatting check, typecheck, tests, and coverage artifact.
- **FR-023**: CI MUST include a deterministic smoke benchmark workflow using a mock model adapter.
- **FR-024**: CI/CD MUST include a manually triggered full benchmark report workflow.
- **FR-025**: CI/CD MUST include a tag-based release workflow with report artifacts, and release publishing MUST be manual-only.
- **FR-026**: Normal pull request CI MUST NOT require GPU, real model downloads, paid APIs, or large audio generation.
- **FR-027**: Generated datasets, audio files, benchmark outputs, model checkpoints, and reports MUST NOT be committed to Git, except small test fixtures and `.gitkeep` files.
- **FR-028**: Benchmark outputs produced by automation MUST be uploaded as retained workflow artifacts rather than committed to Git.
- **FR-029**: Pull requests MUST use a template that links to Speckit task IDs and includes validation evidence.
- **FR-030**: Benchmark Experiment issues MUST capture hypothesis, pipeline, setup, metrics, and result.
- **FR-031**: Tests MUST cover schema validation, parser repair, metrics, and pipeline orchestration.
- **FR-032**: The repository MUST include app areas for the demo user experience, CLI workflows, notebooks, and backend tool execution.
- **FR-033**: Pull request coverage and smoke benchmark artifacts MUST be retained for 14 days.
- **FR-034**: Manual full benchmark and release report artifacts MUST be retained for 90 days.
- **FR-035**: Full audio/model benchmarks, real model runs, paid API runs, large audio generation, report generation, and release publishing MUST be manual-only.
- **FR-036**: GitHub issue templates or issue forms MUST cover Feature Task, Benchmark Experiment, Bug, and Documentation/Process issue types.
- **FR-037**: The smoke benchmark MUST verify all four pipelines using MockModelAdapter.
- **FR-038**: The smoke benchmark MUST include English and Russian examples, tool-required and no-tool examples, invalid JSON cases, invalid schema cases, and written metrics/artifacts.

### Key Entities *(include if feature involves data)*

- **Benchmark Example**: A versioned semantic request item with language, modality links, expected tool decision, expected tool invocation when applicable, and split assignment.
- **Audio Fixture**: A small test audio input linked to a benchmark example for deterministic tests.
- **Pipeline Run**: A recorded execution of one pipeline for one benchmark example, including input reference, raw output, parsed output, validation errors, optional tool result, answer, and metrics.
- **Tool Invocation**: A structured JSON request naming `units.convert` with numeric value, source unit, and target unit.
- **Metric Result**: A measured outcome for a pipeline, such as JSON validity, schema validity, tool-call correctness, transcript quality, answer correctness, and modality-gap comparison.
- **Workflow Artifact**: A retained automation output such as coverage data, smoke benchmark output, or full benchmark report.
- **Pull Request Evidence**: Links and notes proving the PR is tied to Speckit task IDs and has passed required validation.
- **GitHub Issue Type**: A tracked work category for Feature Task, Benchmark Experiment, Bug, or Documentation/Process.
- **Benchmark Experiment Issue**: A tracked benchmark experiment record containing hypothesis, pipeline, setup, metrics, and result.

### Benchmark and Dataset Requirements *(mandatory for benchmark changes)*

- **Dataset Version**: Each generated or curated dataset release has a stable version identifier.
- **Split Strategy**: Train, validation, and test splits are deterministic and reproducible from recorded dataset metadata.
- **Languages**: Russian and English examples are required for benchmark coverage.
- **Modalities**: Text and audio examples share semantic IDs so modality-gap metrics compare equivalent requests.
- **Allowed Tools**: `units.convert` for MVP; weather is not part of MVP.
- **Artifact Logging**: Each experiment saves inputs, raw model outputs, parsed outputs, validation errors, and metrics.
- **Failure Handling**: Invalid JSON, schema validation errors, unsupported tool calls, and failed optional backend execution are recorded as explicit failures.
- **CI Evidence**: Normal pull request validation includes lint, formatting check, typecheck, tests, smoke benchmark, and coverage artifact retained for 14 days.
- **Smoke Benchmark Scope**: The deterministic smoke benchmark covers all four pipelines with MockModelAdapter, English and Russian examples, tool-required and no-tool examples, invalid JSON/schema cases, and written metrics/artifacts.
- **Full Benchmark Trigger**: Full audio/model benchmarks, real model runs, paid API runs, large audio generation, report generation, and release publishing are manual-only.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For a deterministic smoke benchmark, all four pipelines produce recorded outputs and metrics for 100% of included English and Russian examples, including tool-required, no-tool, invalid JSON, and invalid schema cases.
- **SC-002**: For tool-required smoke examples, 100% of successful model outputs are valid JSON before schema validation is attempted.
- **SC-003**: For valid `units.convert` smoke examples, 100% of executed tool calls produce the expected converted value within the documented rounding tolerance.
- **SC-004**: For invalid JSON or invalid schema examples, 100% of failures are logged with raw output and validation details.
- **SC-005**: For paired text/audio examples, 100% of evaluated audio items can be traced to the same semantic example and split as their text counterpart.
- **SC-006**: Normal pull request validation completes without GPU, paid APIs, real model downloads, or large generated audio.
- **SC-007**: Automated benchmark and coverage outputs are available as workflow artifacts for every relevant workflow run with 14-day retention for PR artifacts and 90-day retention for manual full benchmark and release report artifacts.
- **SC-008**: Pull requests include linked Speckit task IDs and validation evidence before review is considered complete.

## Assumptions

- The MVP benchmark scope is limited to unit conversion and direct answers for requests that do not need tools.
- Backend tool execution can be disabled for dry-run evaluation, but schema validation still occurs.
- Small fixtures may be committed when they are required for deterministic tests and are intentionally bounded.
- Full benchmark reports may rely on manually provisioned credentials, models, audio generation, or GPU-capable runners outside normal pull request CI.
- Rounding rules for unit conversion will be documented during planning and applied consistently in metrics.
