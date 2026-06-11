# Tasks: Bilingual Voice Benchmark Demo

**Input**: Design documents from `/specs/002-voice-benchmark-demo/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [quickstart.md](quickstart.md), [contracts/](contracts/)

**Tests**: TDD is required where practical for tool schema validation, tool provider registry/executor behavior, `units.convert` provider behavior, JSON parser and repair, metric calculations, dataset split generation, and pipeline orchestration with mock models.

**Documentation Rule**: Every public class, function, and method introduced by an implementation task must include a concise explanatory docstring or equivalent public API comment before that task is marked complete.

**Organization**: Tasks are grouped by implementation phase, user story, and pipeline. Story labels map to the spec: US1 text unit conversion baseline, US2 audio transcription baseline, US3 one-pass audio tool calling, US4 cascaded audio tool calling, US5 benchmark report and demo review.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and does not depend on incomplete tasks.
- **[Story]**: Required for user story phases only.
- Every task includes an exact repository path.

## Phase 1: Project Scaffold And Configuration

**Purpose**: Create the Python monorepo skeleton, dependency configuration, test configuration, and artifact hygiene needed by every later phase.

- [X] T001 Create Python project metadata with runtime and dev dependencies in `pyproject.toml`
- [X] T002 Configure ruff lint and format settings in `pyproject.toml`
- [X] T003 Configure pytest discovery, markers, and test paths in `pyproject.toml`
- [X] T004 Create package directories with `__init__.py` files under `packages/tool_schema`, `packages/dataset_builder`, `packages/tts_synth`, `packages/model_runner`, `packages/pipeline_runner`, `packages/asr_eval`, `packages/metrics`, and `packages/report_builder`
- [X] T005 Create app package directories with `__init__.py` files under `apps/cli`, `apps/api`, and `apps/notebook`
- [X] T006 [P] Create configuration directories and placeholder README files in `configs/prompts/README.md`, `configs/tools/README.md`, `configs/models/README.md`, and `configs/experiments/README.md`
- [X] T007 [P] Create script entrypoint placeholders in `scripts/generate_dataset.py`, `scripts/synthesize_audio.py`, `scripts/run_benchmark.py`, and `scripts/build_report.py`
- [X] T008 [P] Create test package structure with `tests/unit/__init__.py`, `tests/integration/__init__.py`, and `tests/e2e/__init__.py`
- [X] T009 Configure generated artifact exclusions for `data/generated/`, `runs/`, `reports/*.md`, audio files, model files, checkpoints, `wandb/`, and `mlruns/` in `.gitignore`
- [X] T010 [P] Add tracked artifact placeholder files in `data/raw/.gitkeep`, `data/processed/.gitkeep`, `data/fixtures/.gitkeep`, and `reports/.gitkeep`

---

## Phase 2: Tool Schema, Registry, And Executor (Foundational)

**Purpose**: Implement the validated tool-provider trust boundary before any model output or pipeline can execute a tool.

**Independent Test**: `python -m pytest tests/unit/test_tool_schema.py tests/unit/test_units_executor.py tests/unit/test_tool_registry.py tests/unit/test_tool_executor.py` validates schema acceptance/rejection, provider registration, JSON Schema export, structured failures, and deterministic conversion behavior.

### Tests First

- [X] T011 [P] Create failing Pydantic model and JSON Schema validation tests for valid and invalid model envelopes in `tests/unit/test_tool_schema.py`
- [X] T012 [P] Create failing `units.convert` executor tests for length, mass, temperature, incompatible family, and unsupported unit cases in `tests/unit/test_units_executor.py`
- [X] T013 [P] Create failing JSON Schema contract compatibility test using `specs/002-voice-benchmark-demo/contracts/model-output.schema.json` in `tests/unit/test_model_output_schema_contract.py`
- [X] T013a [P] Create failing `ToolProvider` interface and JSON Schema export tests in `tests/unit/test_tool_provider.py`
- [X] T013b [P] Create failing `ToolRegistry` tests for provider lookup, prompt schema export, unknown tool failures, and duplicate provider names in `tests/unit/test_tool_registry.py`
- [X] T013c [P] Create failing `ToolExecutor` tests for valid execution, invalid argument failures, and provider execution errors in `tests/unit/test_tool_executor.py`
- [X] T013d [P] Create failing `ToolCall`, `ToolResult`, and tool manifest builder tests in `tests/unit/test_tool_manifest.py`
- [X] T013e [P] Create failing pipeline import-boundary test proving `packages/pipeline_runner` does not import concrete tool providers in `tests/unit/test_pipeline_tool_boundaries.py`

### Implementation

- [X] T014 Implement unit enums, `ToolCall`/serialized `tool_call`, `ModelOutputEnvelope`, and validation error models in `packages/tool_schema/models.py`
- [X] T015 Implement strict JSON Schema loading and validation helpers in `packages/tool_schema/json_schema.py`
- [X] T016 Implement deterministic `units.convert` executor with compatible-family checks in `packages/tool_schema/executor.py`
- [X] T017 Export tool schema and executor APIs from `packages/tool_schema/__init__.py`
- [X] T018 Add checked-in tool schema copy for runtime/config consumers in `configs/tools/model-output.schema.json`
- [X] T018a Implement `ToolProvider`, `ToolRegistry`, `ToolExecutor`, and structured tool failure models in `packages/tool_schema/providers.py`
- [X] T018b Adapt `units.convert` into a `ToolProvider` with Pydantic argument schema and JSON Schema export in `packages/tool_schema/units.py`
- [X] T018c Export registered tool prompt/validation schemas from `packages/tool_schema/json_schema.py` and `configs/tools/model-output.schema.json`
- [X] T018d Export provider registry and executor APIs from `packages/tool_schema/__init__.py`
- [X] T018e Implement `ToolCall`, `ToolResult`, `ToolManifest`, and registry-backed manifest builder in `packages/tool_schema/providers.py`

**Checkpoint**: Tool calls can be parsed, resolved, validated, rejected, and executed deterministically through the registry/executor boundary without any pipeline knowing concrete tool implementations.

---

## Phase 3: Synthetic Dataset Builder (US1, US2, US3, US4)

**Purpose**: Generate the bilingual JSONL dataset used by all text and audio benchmark modes.

**Independent Test**: `python -m pytest tests/unit/test_dataset_builder.py tests/integration/test_generate_dataset_cli.py` verifies 240 examples, language balance, no-tool ratio, deterministic splits, expected outputs, and CLI artifact writing.

### Tests First

- [X] T019 [P] [US1] Create failing dataset balance and expected-field tests in `tests/unit/test_dataset_builder.py`
- [X] T020 [P] [US1] Create failing deterministic split generation tests stratified by language, tool/no-tool label, and unit family in `tests/unit/test_dataset_splits.py`
- [X] T021 [P] [US1] Create failing dataset CLI contract test for `voxtool dataset generate` behavior in `tests/integration/test_generate_dataset_cli.py`

### Implementation

- [X] T022 [P] [US1] Implement dataset record models for `BenchmarkExample` and generation metadata in `packages/dataset_builder/models.py`
- [X] T023 [US1] Implement deterministic unit-conversion and no-tool template generation in `packages/dataset_builder/generator.py`
- [X] T024 [US1] Implement deterministic 70/15/15 stratified split assignment in `packages/dataset_builder/splits.py`
- [X] T025 [US1] Implement JSONL read/write helpers for dataset records in `packages/dataset_builder/io.py`
- [X] T026 [US1] Implement dataset generation CLI command in `apps/cli/dataset.py`
- [X] T027 [US1] Wire dataset script entrypoint to CLI command in `scripts/generate_dataset.py`
- [X] T028 [US1] Add small deterministic dataset fixture for tests in `data/fixtures/examples.small.jsonl`

**Checkpoint**: Pipeline A can be tested against a deterministic generated text dataset before audio support exists.

---

## Phase 4: Prompt Templates And Parser (US1, US3, US4)

**Purpose**: Define prompts for pipelines A-D and implement raw model output parsing, one repair attempt, and validation logging.

**Independent Test**: `python -m pytest tests/unit/test_json_parser.py tests/unit/test_prompt_templates.py` verifies prompt availability, first-pass parsing, repair behavior, and validation error recording.

### Tests First

- [X] T029 [P] [US1] Create failing JSON parser tests for valid first-pass envelopes, invalid JSON, single repair success, and failed repair in `tests/unit/test_json_parser.py`
- [X] T030 [P] [US1] Create failing parser validation tests for no-tool envelope consistency, non-null false-alarm tool calls, unknown tools, and invalid tool arguments in `tests/unit/test_parser_validation.py`
- [X] T031 [P] [US1] Create failing prompt template tests proving tool prompts are built from registered tool manifests in `tests/unit/test_prompt_templates.py`

### Implementation

- [X] T032 [US1] Implement parser result models and parser orchestration in `packages/tool_schema/parser.py`
- [X] T033 [US1] Implement single-attempt JSON repair strategy in `packages/tool_schema/repair.py`
- [X] T034 [US1] Add text tool-calling prompt template in `configs/prompts/pipeline_a_text_tool.md`
- [X] T035 [P] [US2] Add audio transcript prompt template in `configs/prompts/pipeline_b_transcript.md`
- [X] T036 [P] [US3] Add one-pass audio tool-calling prompt template in `configs/prompts/pipeline_c_audio_tool.md`
- [X] T037 [P] [US4] Add cascaded transcript-to-tool prompt template in `configs/prompts/pipeline_d_transcript_tool.md`
- [X] T038 [US1] Implement prompt loading and registry-backed tool manifest injection helpers in `packages/model_runner/prompts.py`

**Checkpoint**: Model outputs can be parsed and validated consistently before any real pipeline is implemented.

---

## Phase 5: Pipeline A Text Benchmark (US1)

**Goal**: Run text input through prompt, model, parse/validate, optional tool execution, and final answer recording.

**Independent Test**: Run Pipeline A with `MockModelAdapter` on generated text examples and verify raw outputs, parsed envelopes, validation errors, optional execution results, final answers, and text tool-use metrics.

### Tests First

- [X] T039 [P] [US1] Create failing `MockModelAdapter` tests for valid tool, no-tool, invalid JSON, repaired JSON, and invalid schema outputs in `tests/unit/test_mock_model_adapter.py`
- [X] T040 [P] [US1] Create failing Pipeline A orchestration test with mock examples and registry/executor-only tool calls in `tests/integration/test_pipeline_a.py`
- [X] T041 [P] [US1] Create failing artifact writer tests for raw output, parsed output, validation error, structured failures, and execution result JSONL records in `tests/unit/test_pipeline_artifacts.py`

### Implementation

- [X] T042 [P] [US1] Define model adapter protocols and output types in `packages/model_runner/base.py`
- [X] T043 [US1] Implement deterministic `MockModelAdapter` in `packages/model_runner/mock.py`
- [X] T044 [P] [US1] Implement `TextLLMAdapter` placeholder interface for transcript-to-tool-call experiments in `packages/model_runner/text_llm.py`
- [X] T045 [US1] Implement shared pipeline artifact writer in `packages/pipeline_runner/artifacts.py`
- [X] T046 [US1] Implement Pipeline A orchestration using only `ToolRegistry` and `ToolExecutor` for tool calls in `packages/pipeline_runner/pipeline_a.py`
- [X] T047 [US1] Implement benchmark runner dispatch for Pipeline A in `packages/pipeline_runner/runner.py`
- [X] T048 [US1] Implement benchmark CLI command for text pipeline execution in `apps/cli/benchmark.py`
- [X] T049 [US1] Wire benchmark script entrypoint in `scripts/run_benchmark.py`

**Checkpoint**: US1 MVP is independently functional for at least 200 text examples.

---

## Phase 6: TTS Audio Dataset Generation (US2, US3, US4)

**Goal**: Produce synthesized audio metadata and local audio fixtures linked to every text example.

**Independent Test**: Generate audio metadata from the dataset and verify one audio record per text example, stable ID linkage, split inheritance, reference transcript, and synthesis settings.

### Tests First

- [X] T050 [P] [US2] Create failing audio metadata model and JSONL tests in `tests/unit/test_audio_metadata.py`
- [X] T051 [P] [US2] Create failing TTS synthesis adapter tests using a deterministic local/silent fixture synthesizer in `tests/unit/test_tts_synth.py`
- [X] T052 [P] [US2] Create failing audio synthesis CLI contract test in `tests/integration/test_synthesize_audio_cli.py`

### Implementation

- [X] T053 [P] [US2] Implement `AudioExample` and synthesis settings models in `packages/tts_synth/models.py`
- [X] T054 [US2] Implement deterministic local fixture synthesizer in `packages/tts_synth/synthesizer.py`
- [X] T055 [US2] Implement audio metadata JSONL writer in `packages/tts_synth/io.py`
- [X] T056 [US2] Implement audio synthesis CLI command in `apps/cli/audio.py`
- [X] T057 [US2] Wire audio synthesis script entrypoint in `scripts/synthesize_audio.py`
- [X] T058 [US2] Add tiny committed audio fixture or metadata-only fixture for tests in `data/fixtures/audio/README.md`

**Checkpoint**: Audio dataset generation is reproducible and linked to text examples without requiring cloud services.

---

## Phase 7: Pipeline B ASR Benchmark (US2)

**Goal**: Run audio input through ASR/model transcript generation and report WER.

**Independent Test**: Run Pipeline B with a mock ASR adapter on audio metadata and verify transcript outputs, normalization, WER by language, and artifact writing.

### Tests First

- [X] T059 [P] [US2] Create failing transcript normalization and WER tests for Russian and English in `tests/unit/test_asr_eval.py`
- [X] T060 [P] [US2] Create failing `ASRAdapter` protocol/mock tests in `tests/unit/test_asr_adapter.py`
- [X] T061 [P] [US2] Create failing Pipeline B orchestration test in `tests/integration/test_pipeline_b.py`

### Implementation

- [X] T062 [P] [US2] Implement transcript normalization helpers in `packages/asr_eval/normalization.py`
- [X] T063 [US2] Implement WER calculation wrapper around jiwer in `packages/asr_eval/wer.py`
- [X] T064 [US2] Implement `ASRAdapter` interface and deterministic mock behavior in `packages/model_runner/asr.py`
- [X] T065 [US2] Implement Pipeline B orchestration in `packages/pipeline_runner/pipeline_b.py`
- [X] T066 [US2] Extend benchmark runner dispatch for Pipeline B in `packages/pipeline_runner/runner.py`
- [X] T067 [US2] Extend benchmark CLI audio arguments for Pipeline B in `apps/cli/benchmark.py`

**Checkpoint**: US2 is independently functional for transcript-only audio baseline and WER evaluation.

---

## Phase 8: Pipelines C And D Audio Tool-Use Benchmark (US3, US4)

**Goal**: Run one-pass audio tool calling and cascaded ASR-to-text tool calling with shared parser, validation, and metrics artifacts.

**Independent Test**: Run Pipelines C and D with deterministic mock adapters and verify transcript, raw output, parsed envelope, validation error, optional execution, and per-example artifact records.

### Tests First

- [X] T068 [P] [US3] Create failing `Gemma3nAdapter` capability and mock audio-output tests in `tests/unit/test_gemma3n_adapter.py`
- [X] T069 [P] [US3] Create failing Pipeline C orchestration test with registry/executor-only tool calls in `tests/integration/test_pipeline_c.py`
- [X] T070 [P] [US4] Create failing Pipeline D orchestration test combining ASR, TextLLM adapters, and registry/executor-only tool calls in `tests/integration/test_pipeline_d.py`
- [X] T071 [P] [US4] Create failing all-pipelines smoke orchestration test with `MockModelAdapter` in `tests/e2e/test_all_pipelines_smoke.py`

### Implementation

- [X] T072 [P] [US3] Implement `Gemma3nAdapter` interface and local/manual-run placeholder behavior in `packages/model_runner/gemma3n.py`
- [X] T073 [US3] Implement Pipeline C orchestration using only `ToolRegistry` and `ToolExecutor` for tool calls in `packages/pipeline_runner/pipeline_c.py`
- [X] T074 [US4] Implement Pipeline D orchestration using only `ToolRegistry` and `ToolExecutor` for tool calls in `packages/pipeline_runner/pipeline_d.py`
- [X] T075 [US3] Extend benchmark runner dispatch for Pipelines C and D in `packages/pipeline_runner/runner.py`
- [X] T076 [US4] Extend benchmark CLI pipeline selection for A-D in `apps/cli/benchmark.py`
- [X] T077 [US3] Add experiment config examples for mock and manual Gemma3n runs in `configs/experiments/audio_tool_use.yml`

**Checkpoint**: US3 and US4 are independently testable on audio examples with deterministic mock adapters.

---

## Phase 9: Metrics Aggregation And Report Builder (US5)

**Goal**: Aggregate all required tool-use and ASR metrics, compute modality gap, and generate the final markdown report with failure analysis.

**Independent Test**: Build a report from deterministic smoke artifacts and verify dataset summary, per-pipeline metrics, language splits, confusion matrix, WER, modality gap, best-pipeline rationale, and categorized failures.

### Tests First

- [ ] T078 [P] [US5] Create failing tool metric tests for parsability rate, repair success rate, tool decision accuracy, confusion matrix, precision, recall, and false alarm rate in `tests/unit/test_tool_metrics.py`
- [ ] T079 [P] [US5] Create failing exact match and per-field argument metric tests for partially correct calls in `tests/unit/test_exact_match_metrics.py`
- [ ] T080 [P] [US5] Create failing modality gap metric tests using paired text/audio example IDs in `tests/unit/test_modality_gap.py`
- [ ] T081 [P] [US5] Create failing report builder contract test in `tests/integration/test_report_builder.py`

### Implementation

- [ ] T082 [P] [US5] Implement tool-use metric calculations in `packages/metrics/tool_use.py`
- [ ] T083 [P] [US5] Implement modality gap calculations in `packages/metrics/modality_gap.py`
- [ ] T084 [US5] Implement metrics aggregation with pandas and CSV/Parquet output in `packages/metrics/aggregation.py`
- [ ] T085 [US5] Implement failure case categorization in `packages/metrics/failure_cases.py`
- [ ] T086 [US5] Implement report tables and best-pipeline selection logic in `packages/report_builder/report.py`
- [ ] T087 [P] [US5] Implement matplotlib plot helpers for report artifacts in `packages/report_builder/plots.py`
- [ ] T088 [US5] Implement report CLI command in `apps/cli/report.py`
- [ ] T089 [US5] Wire report script entrypoint in `scripts/build_report.py`

**Checkpoint**: US5 report review is independently functional from saved benchmark artifacts.

---

## Phase 10: Optional API Demo (US5)

**Goal**: Provide a small local FastAPI backend for text and audio demo execution without building a complex UI.

**Independent Test**: API contract tests exercise `/demo/text` and `/demo/audio` with mock adapters and verify parsed output, validation error, optional execution result, and final answer response shape.

### Tests First

- [ ] T090 [P] [US5] Create failing optional API contract tests for `/demo/text` in `tests/integration/test_api_text_demo.py`
- [ ] T091 [P] [US5] Create failing optional API contract tests for `/demo/audio` in `tests/integration/test_api_audio_demo.py`

### Implementation

- [ ] T092 [US5] Implement FastAPI app factory and dependency wiring in `apps/api/main.py`
- [ ] T093 [US5] Implement `/demo/text` route using only `ToolRegistry` and `ToolExecutor` for tool calls in `apps/api/routes_text.py`
- [ ] T094 [US5] Implement `/demo/audio` route using only `ToolRegistry` and `ToolExecutor` for tool calls in `apps/api/routes_audio.py`
- [ ] T095 [US5] Add API package entrypoint in `apps/api/__main__.py`

**Checkpoint**: Optional local API supports demo execution but remains secondary to CLI/notebook/report workflows.

---

## Phase 11: Final Notebook And Documentation (US5)

**Goal**: Deliver a runnable demonstration notebook and concise documentation for local benchmark execution and review.

**Independent Test**: Follow `quickstart.md` using mock adapters and open the notebook to inspect Russian and English text/audio examples, parsed JSON, optional execution, metrics, and report links.

- [ ] T096 [P] [US5] Create final demo notebook with text, audio, pipeline, metrics, and report cells in `apps/notebook/voice_benchmark_demo.ipynb`
- [ ] T097 [P] [US5] Add notebook helper module for loading artifacts and examples in `apps/notebook/helpers.py`
- [ ] T098 [US5] Update feature quickstart commands and expected artifact paths in `specs/002-voice-benchmark-demo/quickstart.md`
- [ ] T099 [US5] Add repository README section for MVP scope, non-goals, and quickstart in `README.md`
- [ ] T100 [US5] Add CI workflow for ruff, pytest, and mock smoke benchmark in `.github/workflows/ci.yml`
- [ ] T101 [US5] Add smoke benchmark workflow artifact upload for generated metrics in `.github/workflows/benchmark-smoke.yml`
- [ ] T102 [US5] Run final validation commands from `specs/002-voice-benchmark-demo/quickstart.md` and record evidence in `specs/002-voice-benchmark-demo/validation.md`

**Checkpoint**: Documentation, notebook, smoke validation, and PR evidence are ready.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1**: No dependencies.
- **Phase 2**: Depends on Phase 1 and blocks all user-story implementation.
- **Phase 3**: Depends on Phase 2; enables text benchmark data for US1.
- **Phase 4**: Depends on Phase 2; should complete before Pipelines A, C, and D.
- **Phase 5**: Depends on Phases 3 and 4; delivers US1 MVP for Pipeline A.
- **Phase 6**: Depends on Phase 3; enables audio work for US2-US4.
- **Phase 7**: Depends on Phase 6; delivers Pipeline B and WER.
- **Phase 8**: Depends on Phases 4, 6, and 7; delivers Pipelines C and D.
- **Phase 9**: Depends on Phases 5, 7, and 8; delivers aggregate metrics/report.
- **Phase 10**: Depends on Phases 5, 7, and 8; optional after core pipelines exist.
- **Phase 11**: Depends on Phases 5, 7, 8, and 9.

### User Story Dependencies

- **US1 Text Unit Conversion Baseline**: Requires foundational schema, dataset, parser, and Pipeline A.
- **US2 Audio Transcription Baseline**: Requires dataset and TTS metadata; independent of tool-call execution.
- **US3 One-Pass Audio Tool Calling**: Requires audio dataset, parser, and Pipeline C.
- **US4 Cascaded Audio Tool Calling**: Requires ASR transcript path, parser, and Pipeline D.
- **US5 Benchmark Report and Demo Review**: Requires artifacts from US1-US4; API is optional.

### Pipeline Mapping

- **Pipeline A**: T039-T049 plus metrics in T078-T089.
- **Pipeline B**: T059-T067 plus WER/report tasks T078-T089.
- **Pipeline C**: T068-T073, T075, T077 plus metrics/report tasks T078-T089.
- **Pipeline D**: T070-T071, T074-T077 plus metrics/report tasks T078-T089.

---

## Parallel Execution Examples

### Phase 2 Tests

```text
Task: T011 Create failing Pydantic model and JSON Schema validation tests in tests/unit/test_tool_schema.py
Task: T012 Create failing units.convert executor tests in tests/unit/test_units_executor.py
Task: T013 Create failing JSON Schema contract compatibility test in tests/unit/test_model_output_schema_contract.py
```

### Dataset And Parser Work

```text
Task: T019 Create failing dataset balance and expected-field tests in tests/unit/test_dataset_builder.py
Task: T020 Create failing deterministic split generation tests in tests/unit/test_dataset_splits.py
Task: T029 Create failing JSON parser tests in tests/unit/test_json_parser.py
Task: T031 Create failing prompt template tests in tests/unit/test_prompt_templates.py
```

### Audio Pipeline Work

```text
Task: T059 Create failing transcript normalization and WER tests in tests/unit/test_asr_eval.py
Task: T068 Create failing Gemma3nAdapter capability tests in tests/unit/test_gemma3n_adapter.py
Task: T070 Create failing Pipeline D orchestration test in tests/integration/test_pipeline_d.py
```

### Metrics And Report Work

```text
Task: T078 Create failing tool metric tests in tests/unit/test_tool_metrics.py
Task: T079 Create failing exact match metric tests in tests/unit/test_exact_match_metrics.py
Task: T080 Create failing modality gap metric tests in tests/unit/test_modality_gap.py
Task: T081 Create failing report builder contract test in tests/integration/test_report_builder.py
```

---

## Implementation Strategy

### MVP First

1. Complete Phase 1.
2. Complete Phase 2.
3. Complete Phase 3.
4. Complete Phase 4.
5. Complete Phase 5 for Pipeline A.
6. Stop and validate US1 with mock adapters on at least 200 text examples.

### Incremental Delivery

1. Add Phase 6 and Phase 7 for audio transcript baseline and WER.
2. Add Phase 8 for Pipelines C and D audio tool-use metrics.
3. Add Phase 9 for aggregate report and failure analysis.
4. Add Phase 10 only if local API demo execution is needed.
5. Add Phase 11 for final notebook, docs, and CI evidence.

### TDD Rule

For tasks with a paired test and implementation path, complete the test task first and verify it fails for the expected reason before implementing the corresponding package, app, or script task.

### Public API Documentation Rule

Before marking an implementation task complete, confirm newly introduced public classes, functions, and methods have concise explanatory docstrings or equivalent public API comments.

### Non-Goals Guardrails

- Do not implement weather behavior in any path.
- Do not require cloud services for MVP validation.
- Do not build a complex UI.
- Do not commit generated datasets, audio, benchmark runs, model files, checkpoints, or generated reports outside bounded fixtures and placeholders.
