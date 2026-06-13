# Tasks: Advanced Benchmark Phases

**Input**: Design documents from `/specs/003-advanced-benchmark-phases/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: Required for schema validation, parser repair, metrics, pipeline orchestration, dataset generation, model running, speech output, tool execution, and report generation. Real model downloads, LoRA training, speech engines, and quantized inference are not required in normal CI.

**Organization**: Tasks are grouped into the three requested implementation phases. Each phase maps to the corresponding user story: US1 real adapters and Colab demo, US2 LoRA fine-tuning and Russian dataset, US3 speech output, multiple tools, and quantization.

## Phase 1: Shared Setup And CI Boundaries

**Purpose**: Establish package/config/test scaffolding and CI boundaries that all three implementation phases depend on.

- [X] T001 Create advanced roadmap fixture directory placeholders in `data/fixtures/advanced/.gitkeep`
- [X] T002 [P] Create model config directory placeholders in `configs/models/.gitkeep`
- [X] T003 [P] Create fine-tuning config directory placeholders in `configs/finetuning/.gitkeep`
- [X] T004 [P] Create dataset config directory placeholders in `configs/datasets/.gitkeep`
- [X] T005 [P] Create inference config directory placeholders in `configs/inference/.gitkeep`
- [X] T006 [P] Create advanced experiment config placeholder in `configs/experiments/advanced_smoke.yaml`
- [X] T007 Add optional dependency groups for notebook/model/fine-tuning/speech/quantization without enabling them in default CI in `pyproject.toml`
- [X] T008 Add or update generated artifact ignore rules for model caches, checkpoints, generated speech, LoRA runs, and quantized runs in `.gitignore`
- [X] T009 Add normal CI guard comments that real model downloads are forbidden in `.github/workflows/ci.yml`
- [X] T010 [P] Add manual GPU benchmark workflow skeleton using `workflow_dispatch` in `.github/workflows/gpu-benchmarks.yml`

**Checkpoint**: Shared paths and CI resource boundaries are documented before feature implementation begins.

---

## Phase 2: Foundational Benchmark Interfaces

**Purpose**: Build shared abstractions needed by all three roadmap phases while preserving the benchmark JSON and tool-validation trust boundary.

- [X] T011 [P] Add test package marker for model runner adapter tests in `tests/unit/model_runner/__init__.py` (flat layout: covered by existing `tests/unit/__init__.py`)
- [X] T012 [P] Add test package marker for fine-tuning tests in `tests/unit/finetuning/__init__.py` (flat layout: covered by existing `tests/unit/__init__.py`)
- [X] T013 [P] Add test package marker for speech output tests in `tests/unit/speech_output/__init__.py` (flat layout: covered by existing `tests/unit/__init__.py`)
- [X] T014 [P] Add test package marker for advanced metrics tests in `tests/unit/metrics/__init__.py` (flat layout: covered by existing `tests/unit/__init__.py`)
- [X] T015 [P] Add test package marker for advanced pipeline tests in `tests/integration/pipeline_runner/__init__.py` (flat layout: covered by existing `tests/integration/__init__.py`)
- [X] T016 [P] Write failing tests for canonical model response parsing and raw-output retention in `tests/unit/test_model_response.py`
- [X] T017 [P] Write failing tests for adapter capability selection and unsupported-runtime failures in `tests/unit/test_adapter_capabilities.py`
- [X] T018 [P] Write failing tests for advanced metric aggregation fields in `tests/unit/test_advanced_metrics.py`
- [X] T019 [P] Write failing tests for advanced pipeline artifact fields in `tests/integration/test_advanced_pipeline_artifacts.py`
- [X] T020 Define `ModelResponse` and adapter capability models in `packages/model_runner/adapters/base.py`
- [X] T021 Export adapter base interfaces from `packages/model_runner/adapters/__init__.py`
- [X] T022 Add advanced metric result helpers for per-tool, Russian-only, delta, latency, and memory-note fields in `packages/metrics/advanced.py`
- [X] T023 Add advanced pipeline artifact field support for adapter IDs, capabilities, profiles, manifest snapshots, speech output, and runtime skips in `packages/pipeline_runner/artifacts.py`
- [X] T024 Add advanced smoke fixture with no real model dependency in `data/fixtures/advanced/sample_text.jsonl`

**Checkpoint**: Shared interfaces and fixtures are ready; each roadmap phase can proceed with mock-backed tests.

---

## Phase 3: Real Model Adapters And Colab Demo (Priority: P1) 🎯 MVP

**Goal**: Add Voxtral, Qwen, and Gemma adapters behind the common adapter interface, keep normal CI mock-only, and provide a Colab notebook that demonstrates text inference and optional audio.

**Independent Test**: Run adapter import/config tests and a mock-backed Pipeline A smoke run without downloading real models, then open `apps/notebook/colab_demo.ipynb` and verify the documented cells select an adapter config, run text examples, validate JSON, execute tools, show final answers, and display metrics.

### Tests For Phase 1

- [X] T025 [P] [US1] Write failing import/config tests for Voxtral adapter and `configs/models/voxtral.yaml` in `tests/unit/model_runner/test_voxtral_adapter_config.py`
- [X] T026 [P] [US1] Write failing import/config tests for Qwen adapter and `configs/models/qwen.yaml` in `tests/unit/model_runner/test_qwen_adapter_config.py`
- [X] T027 [P] [US1] Write failing import/config tests for Gemma adapter and `configs/models/gemma.yaml` in `tests/unit/model_runner/test_gemma_adapter_config.py`
- [X] T028 [P] [US1] Write failing adapter contract tests using `MockModelAdapter` in `tests/unit/model_runner/test_model_adapter_contract.py`
- [X] T029 [P] [US1] Write failing Pipeline A mock adapter integration test in `tests/integration/pipeline_runner/test_pipeline_a_model_adapter.py`
- [X] T030 [P] [US1] Write failing Pipeline C/D capability skip tests with mock audio capability declarations in `tests/integration/pipeline_runner/test_audio_adapter_capabilities.py`
- [X] T031 [P] [US1] Write failing notebook structure smoke test that does not execute real model downloads in `tests/e2e/test_colab_demo_notebook.py`

### Implementation For Phase 1

- [X] T032 [P] [US1] Implement `VoxtralAdapter` import-safe class in `packages/model_runner/voice_toolbench_model_runner/adapters/voxtral.py`
- [X] T033 [P] [US1] Implement `QwenAdapter` import-safe class in `packages/model_runner/voice_toolbench_model_runner/adapters/qwen.py`
- [X] T034 [P] [US1] Implement `GemmaAdapter` import-safe class in `packages/model_runner/voice_toolbench_model_runner/adapters/gemma.py`
- [X] T035 [P] [US1] Add Voxtral adapter config with no eager model download in `configs/models/voxtral.yaml`
- [X] T036 [P] [US1] Add Qwen adapter config with no eager model download in `configs/models/qwen.yaml`
- [X] T037 [P] [US1] Add Gemma adapter config with no eager model download in `configs/models/gemma.yaml`
- [X] T038 [US1] Add adapter registry loading from config in `packages/model_runner/voice_toolbench_model_runner/registry.py`
- [X] T039 [US1] Wire adapter registry selection into benchmark execution in `scripts/run_benchmark.py`
- [X] T040 [US1] Wire adapter registry selection into CLI benchmark command in `apps/cli/voice_toolbench_cli/benchmark.py`
- [X] T041 [US1] Preserve raw output, parsed JSON, validation results, execution results, final answers, and metrics for real adapters in `packages/pipeline_runner/voice_toolbench_pipeline_runner/runner.py`
- [X] T042 [US1] Add structured runtime skip handling for unsupported audio adapters in `packages/pipeline_runner/voice_toolbench_pipeline_runner/capabilities.py`
- [X] T043 [US1] Add Colab demo notebook with dependency install, repo load, adapter selection, text run, optional audio upload, validation, execution, final answer, and metrics in `apps/notebook/colab_demo.ipynb`
- [X] T044 [US1] Add Colab demo helper module for notebook-safe execution in `apps/notebook/colab_demo_helpers.py`
- [X] T045 [US1] Document manual full real-model benchmark and GPU workflow usage in `docs/advanced_real_model_runs.md`

**Checkpoint**: Phase 1 is independently testable with mocks/import checks in CI and manually demonstrable in Colab with at least one real adapter.

---

## Phase 4: LoRA Fine-Tuning And Russian Dataset (Priority: P2)

**Goal**: Add optional LoRA/SFT data preparation, config, training, and evaluation workflows with Russian-focused metrics and no CI training requirement.

**Independent Test**: Build a small SFT JSONL fixture from Russian dataset configs, validate each `expected_output_json` against the benchmark ModelOutput contract, run mock base-vs-LoRA evaluation on paired examples, and confirm Russian, English, no-tool, and per-tool subset metrics are reported.

### Tests For Phase 2

- [ ] T046 [P] [US2] Write failing SFT record schema tests in `tests/unit/finetuning/test_sft_dataset_schema.py`
- [ ] T047 [P] [US2] Write failing deterministic split tests for Russian SFT data in `tests/unit/finetuning/test_sft_splits.py`
- [ ] T048 [P] [US2] Write failing LoRA config validation tests for Gemma and Qwen configs in `tests/unit/finetuning/test_lora_config.py`
- [ ] T049 [P] [US2] Write failing mock training entrypoint tests that do not train a real model in `tests/unit/finetuning/test_train_lora_mock.py`
- [ ] T050 [P] [US2] Write failing base-vs-LoRA evaluation metric tests in `tests/unit/finetuning/test_evaluate_lora.py`
- [ ] T051 [P] [US2] Write failing CLI smoke tests for SFT dataset build, train, and evaluate commands in `tests/integration/test_finetuning_cli.py`

### Implementation For Phase 2

- [ ] T052 [P] [US2] Create fine-tuning package marker in `packages/finetuning/voice_toolbench_finetuning/__init__.py`
- [ ] T053 [US2] Implement SFT dataset conversion and validation in `packages/finetuning/voice_toolbench_finetuning/dataset.py`
- [ ] T054 [US2] Implement LoRA config models in `packages/finetuning/voice_toolbench_finetuning/lora_config.py`
- [ ] T055 [US2] Implement optional LoRA training orchestration with mock/dry-run mode in `packages/finetuning/voice_toolbench_finetuning/train.py`
- [ ] T056 [US2] Implement base-vs-LoRA evaluation and subset metric grouping in `packages/finetuning/voice_toolbench_finetuning/evaluate.py`
- [ ] T057 [P] [US2] Add SFT dataset build script in `scripts/build_sft_dataset.py`
- [ ] T058 [P] [US2] Add optional LoRA training script in `scripts/train_lora.py`
- [ ] T059 [P] [US2] Add LoRA evaluation script in `scripts/evaluate_lora.py`
- [ ] T060 [P] [US2] Add Gemma LoRA config in `configs/finetuning/lora_gemma.yaml`
- [ ] T061 [P] [US2] Add Qwen LoRA config in `configs/finetuning/lora_qwen.yaml`
- [ ] T062 [P] [US2] Add Russian units conversion dataset config in `configs/datasets/ru_units_convert.yaml`
- [ ] T063 [P] [US2] Add Russian ToolBench dataset config in `configs/datasets/ru_toolbench.yaml`
- [ ] T064 [US2] Add CLI dataset build-sft command in `apps/cli/voice_toolbench_cli/dataset.py`
- [ ] T065 [US2] Add CLI train lora command in `apps/cli/voice_toolbench_cli/train.py`
- [ ] T066 [US2] Add CLI eval lora command in `apps/cli/voice_toolbench_cli/eval.py`
- [ ] T067 [US2] Add report-builder support for base model, LoRA model, Russian subset, English subset, no-tool subset, per-tool subset, and deltas in `packages/report_builder/voice_toolbench_report_builder/finetuning.py`
- [ ] T068 [US2] Document optional training and external checkpoint artifact policy in `docs/lora_russian_dataset.md`

**Checkpoint**: Phase 2 is independently testable with generated SFT fixtures and mock evaluation; real LoRA training remains manual.

---

## Phase 5: Speech Output, Multiple Tools, And Quantization (Priority: P3)

**Goal**: Add optional final-answer speech output, expand strict registry-backed tool execution to three tools, and support selectable quantized inference profiles with comparison metrics.

**Independent Test**: Run mock speech synthesis, multi-tool benchmark fixtures, and quantized-profile comparison fixtures without real speech engines, model downloads, or GPU resources in normal CI.

### Tests For Phase 3

- [ ] T069 [P] [US3] Write failing tool registry component tests for `ToolDefinition`, `ToolRegistry`, `ToolExecutor`, and `ToolSchemaValidator` in `tests/unit/tool_schema/test_tool_registry_components.py`
- [ ] T070 [P] [US3] Write failing `text.stress_ru` schema and executor tests in `tests/unit/tool_schema/test_text_stress_ru_tool.py`
- [ ] T071 [P] [US3] Write failing `calculator.simple` schema and executor tests in `tests/unit/tool_schema/test_calculator_simple_tool.py`
- [ ] T072 [P] [US3] Write failing per-tool metrics grouping tests in `tests/unit/metrics/test_per_tool_metrics.py`
- [ ] T073 [P] [US3] Write failing speech synthesizer interface and mock artifact tests in `tests/unit/speech_output/test_speech_synthesizer.py`
- [ ] T074 [P] [US3] Write failing speech manifest writer tests in `tests/unit/speech_output/test_audio_manifest.py`
- [ ] T075 [P] [US3] Write failing quantized profile config tests in `tests/unit/model_runner/test_inference_profiles.py`
- [ ] T076 [P] [US3] Write failing quantization comparison metric tests in `tests/unit/metrics/test_quantization_comparison.py`
- [ ] T077 [P] [US3] Write failing multi-tool Pipeline A integration test in `tests/integration/pipeline_runner/test_multitool_pipeline.py`

### Implementation For Phase 3

- [ ] T078 [US3] Implement `ToolDefinition`, `ToolRegistry`, `ToolExecutor`, and `ToolSchemaValidator` in `packages/tool_schema/voice_toolbench_tool_schema/registry.py`
- [ ] T079 [P] [US3] Implement `units.convert` provider definition using the registry contract in `packages/tool_schema/voice_toolbench_tool_schema/tools/units_convert.py`
- [ ] T080 [P] [US3] Implement `text.stress_ru` provider with Pydantic args, JSON schema, deterministic executor, examples, and metrics grouping in `packages/tool_schema/voice_toolbench_tool_schema/tools/text_stress_ru.py`
- [ ] T081 [P] [US3] Implement `calculator.simple` provider with Pydantic args, JSON schema, deterministic executor, examples, and metrics grouping in `packages/tool_schema/voice_toolbench_tool_schema/tools/calculator_simple.py`
- [ ] T082 [US3] Export supported tool manifests for all three tools in `configs/tools/advanced_tools.json`
- [ ] T083 [US3] Wire multi-tool registry selection into pipeline execution in `packages/pipeline_runner/voice_toolbench_pipeline_runner/tool_execution.py`
- [ ] T084 [US3] Add per-tool metric aggregation in `packages/metrics/voice_toolbench_metrics/per_tool.py`
- [ ] T085 [P] [US3] Create speech output package marker in `packages/speech_output/voice_toolbench_speech_output/__init__.py`
- [ ] T086 [US3] Implement `SpeechSynthesizer` interface and mock synthesizer in `packages/speech_output/voice_toolbench_speech_output/synthesizer.py`
- [ ] T087 [US3] Implement `PiperSpeechSynthesizer` or `EdgeTtsSpeechSynthesizer` adapter without enabling it in CI by default in `packages/speech_output/voice_toolbench_speech_output/providers.py`
- [ ] T088 [US3] Implement speech audio manifest writer in `packages/speech_output/voice_toolbench_speech_output/manifest.py`
- [ ] T089 [US3] Integrate optional speech output into pipeline run artifacts in `packages/pipeline_runner/voice_toolbench_pipeline_runner/speech.py`
- [ ] T090 [US3] Add CLI speech synthesize command in `apps/cli/voice_toolbench_cli/speech.py`
- [ ] T091 [P] [US3] Add full precision inference profile config in `configs/inference/full_precision.yaml`
- [ ] T092 [P] [US3] Add 8bit quantized inference profile config in `configs/inference/quantized_8bit.yaml`
- [ ] T093 [P] [US3] Add 4bit quantized inference profile config in `configs/inference/quantized_4bit.yaml`
- [ ] T094 [US3] Implement inference profile loader and compatibility validation in `packages/model_runner/voice_toolbench_model_runner/inference_profiles.py`
- [ ] T095 [US3] Add quantization comparison script in `scripts/compare_quantization.py`
- [ ] T096 [US3] Add CLI quantization evaluation command in `apps/cli/voice_toolbench_cli/eval.py`
- [ ] T097 [US3] Add multi-tool sample fixture covering `units.convert`, `text.stress_ru`, and `calculator.simple` in `data/fixtures/advanced/multitool_sample.jsonl`
- [ ] T098 [US3] Add mock speech fixture manifest in `data/fixtures/advanced/speech_manifest.jsonl`
- [ ] T099 [US3] Add report sections for speech status, per-tool metrics, memory notes, latency, parsable rate, tool-call exact match, and quantization quality delta in `packages/report_builder/voice_toolbench_report_builder/advanced.py`
- [ ] T100 [US3] Document speech, multi-tool, and quantization manual workflows in `docs/speech_multitool_quantization.md`

**Checkpoint**: Phase 3 is independently testable with mock speech, multi-tool fixtures, and config-only quantized comparisons in normal CI.

---

## Phase 6: Polish And Cross-Cutting Validation

**Purpose**: Finalize documentation, validation commands, and public API descriptions across all phases.

- [ ] T101 [P] Add public API description review for adapter modules in `packages/model_runner/voice_toolbench_model_runner/adapters/base.py`
- [ ] T102 [P] Add public API description review for fine-tuning modules in `packages/finetuning/voice_toolbench_finetuning/dataset.py`
- [ ] T103 [P] Add public API description review for speech output modules in `packages/speech_output/voice_toolbench_speech_output/synthesizer.py`
- [ ] T104 [P] Add public API description review for tool registry modules in `packages/tool_schema/voice_toolbench_tool_schema/registry.py`
- [ ] T105 Update advanced quickstart command evidence in `specs/003-advanced-benchmark-phases/quickstart.md`
- [ ] T106 Update README roadmap references for advanced phases in `README.md`
- [ ] T107 Run `uv run ruff check .` and record evidence in `specs/003-advanced-benchmark-phases/validation.md`
- [ ] T108 Run `uv run ruff format --check .` and record evidence in `specs/003-advanced-benchmark-phases/validation.md`
- [ ] T109 Run `uv run mypy` and record evidence in `specs/003-advanced-benchmark-phases/validation.md`
- [ ] T110 Run `uv run pytest` and record evidence in `specs/003-advanced-benchmark-phases/validation.md`
- [ ] T111 Run mock advanced smoke benchmark with no real model downloads and record artifact paths in `specs/003-advanced-benchmark-phases/validation.md`
- [ ] T112 Verify generated datasets, speech audio, model checkpoints, model caches, benchmark runs, and reports remain ignored in `.gitignore`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Shared Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational Interfaces (Phase 2)**: Depends on Phase 1; blocks all user-story implementation.
- **Real Model Adapters And Colab Demo (Phase 3 / US1)**: Depends on Phase 2; recommended MVP.
- **LoRA Fine-Tuning And Russian Dataset (Phase 4 / US2)**: Depends on Phase 2; can run in parallel with US1 after foundation, but benefits from adapter interfaces.
- **Speech Output, Multiple Tools, And Quantization (Phase 5 / US3)**: Depends on Phase 2; can run in parallel with US1/US2 after foundation, with multi-tool dataset additions feeding US2 later.
- **Polish (Phase 6)**: Depends on completed desired implementation phases.

### User Story Dependencies

- **US1**: No dependency on US2 or US3 after foundation; MVP.
- **US2**: No dependency on US1 real downloads; uses adapter contract and mocks in CI.
- **US3**: No dependency on real downloads or LoRA training; uses registry and mock fixtures in CI.

### Test-First Rules

- Test tasks in each phase should be implemented before corresponding production code.
- Real adapter tests in normal CI must be import/config/contract tests only.
- LoRA tests in normal CI must use mock/dry-run training and fixture evaluation only.
- Speech and quantization tests in normal CI must use mock providers, configs, and fixtures only.

## Parallel Execution Examples

### Phase 1 Parallel Setup

```text
T002, T003, T004, T005, T006, and T010 can run in parallel because they touch different config or workflow files.
```

### US1 Parallel Work

```text
T025, T026, T027, T028, T029, T030, and T031 can run in parallel as independent tests.
T032, T033, T034, T035, T036, and T037 can run in parallel after adapter base interfaces are available.
```

### US2 Parallel Work

```text
T046, T047, T048, T049, T050, and T051 can run in parallel as independent tests.
T057, T058, T059, T060, T061, T062, and T063 can run in parallel after the package interfaces are defined.
```

### US3 Parallel Work

```text
T069 through T077 can run in parallel as independent tests.
T079, T080, T081, T085, T091, T092, and T093 can run in parallel after registry and profile interfaces are defined.
```

## Implementation Strategy

### MVP First

1. Complete Phase 1 shared setup.
2. Complete Phase 2 foundational benchmark interfaces.
3. Complete Phase 3 real model adapters and Colab demo.
4. Validate with mock CI tests plus a manual Colab run for at least one real adapter.

### Incremental Delivery

1. Deliver US1 for demonstrable real-adapter execution without changing normal CI resource requirements.
2. Deliver US2 for Russian SFT data and mock-safe LoRA evaluation.
3. Deliver US3 for assistant-mode speech, multi-tool evaluation, and quantized profile comparison.

### CI Safety

Normal CI must not download real models, train LoRA adapters, require GPU, invoke real speech engines, or run quantized inference. Those workflows are manual, `workflow_dispatch`, or self-hosted runner paths only.
