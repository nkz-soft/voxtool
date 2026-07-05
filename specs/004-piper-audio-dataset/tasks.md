# Tasks: Piper Audio Dataset

**Input**: Design documents from `/specs/004-piper-audio-dataset/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Required because this feature changes TTS and dataset generation behavior.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the existing audio synthesis surface for Piper-backed generation while preserving fixture mode.

- [X] T001 Review existing fixture audio behavior and update public contract notes in `specs/004-piper-audio-dataset/contracts/audio-cli.md`
- [X] T002 [P] Add Piper voice asset setup notes to `data/fixtures/audio/README.md`
- [X] T003 [P] Confirm `speech` optional dependency guidance for `piper-tts` in `pyproject.toml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared models, backend selection, and default voice discovery needed before user story implementation.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T004 [P] Add failing settings tests for Piper fields and fixture defaults in `tests/unit/test_audio_metadata.py`
- [X] T005 [P] Add failing backend selection tests for `fixture-silent` and `piper` engines in `tests/unit/test_tts_synth.py`
- [X] T006 Extend `SynthesisSettings` with Piper voice fields and optional synthesis controls in `packages/tts_synth/models.py`
- [X] T007 Define a typed synthesis backend boundary for fixture and Piper implementations in `packages/tts_synth/synthesizer.py`
- [X] T008 Preserve lazy package exports for new Piper synthesizer symbols in `packages/tts_synth/__init__.py`
- [X] T009 Define Piper voice configuration discovery for notebook defaults in `packages/tts_synth/models.py` and `apps/notebook/colab_demo_helpers.py`

**Checkpoint**: Backend settings, engine selection, and default Piper voice discovery are ready for story work.

---

## Phase 3: User Story 1 - Generate test audio from demo text (Priority: P1) MVP

**Goal**: The existing notebook helper call generates real Piper audio records from the bilingual demo dataset when Piper resources are configured.

**Independent Test**: Run the notebook helper flow with mocked Piper synthesis and confirm one Piper audio record per demo example, preserving source metadata and compatibility with `run_audio_demo`.

### Tests for User Story 1

- [X] T010 [P] [US1] Add failing Piper synthesizer WAV/metadata test with mocked Piper voice in `tests/unit/test_tts_synth.py`
- [X] T011 [P] [US1] Add failing notebook helper test for default Piper settings and configured voice discovery in `tests/integration/test_pipeline_a_model_adapter.py`
- [X] T012 [P] [US1] Add failing CLI contract test for `--engine piper`, `--voice`, `--voice-model-path`, and `--voice-config-path` in `tests/integration/test_synthesize_audio_cli.py`

### Implementation for User Story 1

- [X] T013 [US1] Implement `PiperSynthesizer` with lazy `piper-tts` import and WAV output in `packages/tts_synth/synthesizer.py`
- [X] T014 [US1] Route `synthesize_dataset` to fixture or Piper backend based on `SynthesisSettings.engine` in `packages/tts_synth/synthesizer.py`
- [X] T015 [US1] Update `synthesize_demo_audio` to default to discovered Piper settings while accepting explicit fixture settings in `apps/notebook/colab_demo_helpers.py`
- [X] T016 [US1] Add Piper CLI options and pass them into `SynthesisSettings` while keeping CLI default `fixture-silent` in `apps/cli/audio.py`
- [X] T017 [US1] Keep direct script entrypoint compatible with the expanded CLI in `scripts/synthesize_audio.py`
- [X] T018 [US1] Update notebook smoke assertions for the Piper helper call in `tests/e2e/test_colab_demo_notebook.py`

**Checkpoint**: User Story 1 works independently with mocked Piper synthesis and preserves the high-level notebook call.

---

## Phase 4: User Story 2 - Preserve reproducible benchmark artifacts (Priority: P2)

**Goal**: Generated audio metadata is complete, reproducible, and traceable to the source text examples and synthesis settings.

**Independent Test**: Generate the same bounded dataset twice with deterministic mocked Piper output and verify complete metadata, source links, voice fields, and no partial manifest.

### Tests for User Story 2

- [X] T019 [P] [US2] Add failing metadata round-trip test for Piper synthesis settings and voice fields in `tests/unit/test_audio_metadata.py`
- [X] T020 [P] [US2] Add failing deterministic repeated-generation test for Piper metadata in `tests/unit/test_tts_synth.py`
- [X] T021 [P] [US2] Add failing integration test that `audio.jsonl` is written only after all records are synthesized in `tests/integration/test_synthesize_audio_cli.py`

### Implementation for User Story 2

- [X] T022 [US2] Populate Piper `AudioExample` records with engine, voice, sample rate, duration, source IDs, dataset version, language, and split in `packages/tts_synth/synthesizer.py`
- [X] T023 [US2] Derive WAV duration and sample rate from generated Piper files before creating metadata in `packages/tts_synth/synthesizer.py`
- [X] T024 [US2] Write CLI metadata manifest only after successful full-dataset synthesis in `apps/cli/audio.py`
- [X] T025 [US2] Add language-to-voice settings support for bilingual datasets in `packages/tts_synth/models.py`
- [X] T026 [US2] Include Piper engine and voice fields in notebook audio summaries in `apps/notebook/colab_demo_helpers.py`

**Checkpoint**: User Story 2 can be validated independently through repeated bounded generation and metadata inspection.

---

## Phase 5: User Story 3 - Handle unavailable synthesis resources clearly (Priority: P3)

**Goal**: Missing Piper package, missing voice files, invalid input, output collisions, and synthesis failures stop generation with actionable errors and no misleading complete dataset.

**Independent Test**: Run Piper mode with missing mocked resources and invalid inputs, then confirm clear failures, affected examples when available, and no complete manifest.

### Tests for User Story 3

- [X] T027 [P] [US3] Add failing missing `piper-tts` dependency test in `tests/unit/test_tts_synth.py`
- [X] T028 [P] [US3] Add failing missing voice model/config validation test in `tests/unit/test_tts_synth.py`
- [X] T029 [P] [US3] Add failing CLI failure test that no `audio.jsonl` is written for incomplete Piper runs in `tests/integration/test_synthesize_audio_cli.py`
- [X] T030 [P] [US3] Add failing validation tests for empty text, blank text, and duplicate audio paths in `tests/unit/test_tts_synth.py`
- [X] T031 [P] [US3] Add failing CLI test for existing output collision behavior in `tests/integration/test_synthesize_audio_cli.py`

### Implementation for User Story 3

- [X] T032 [US3] Add clear Piper resource validation errors in `packages/tts_synth/synthesizer.py`
- [X] T033 [US3] Include source example identifiers in per-example synthesis failure messages in `packages/tts_synth/synthesizer.py`
- [X] T034 [US3] Surface Piper generation failures as non-zero CLI results without complete manifests in `apps/cli/audio.py`
- [X] T035 [US3] Validate empty input text, duplicate output paths, and existing output collisions before synthesis in `packages/tts_synth/synthesizer.py`
- [X] T036 [US3] Update notebook helper docstring to describe Piper failure behavior in `apps/notebook/colab_demo_helpers.py`

**Checkpoint**: User Story 3 failure paths are independently testable without real Piper assets.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, manual validation instructions, and final quality gates.

- [X] T037 [P] Update manual Piper setup and artifact evidence instructions in `specs/004-piper-audio-dataset/quickstart.md`
- [X] T038 [P] Add concise public descriptions for new or changed package exports in `packages/tts_synth/__init__.py`
- [X] T039 [P] Review generated artifact ignore coverage for Piper voices/audio in `.gitignore`
- [X] T040 Run targeted tests with `uv run python -m pytest tests/unit/test_audio_metadata.py tests/unit/test_tts_synth.py tests/integration/test_synthesize_audio_cli.py tests/integration/test_pipeline_a_model_adapter.py tests/e2e/test_colab_demo_notebook.py`
- [X] T041 Run full quality checks with `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy .`, and `uv run python -m pytest`
- [X] T042 Run bounded fixture smoke command `uv run python scripts/synthesize_audio.py --dataset data/fixtures/examples.small.jsonl --output .tmp/audio-fixture-check --engine fixture-silent`
- [X] T043 Document manual Piper synthesis artifact path or skipped-resource reason in `specs/004-piper-audio-dataset/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational and is the MVP.
- **User Story 2 (Phase 4)**: Depends on Foundational; can run after US1 tests define the Piper path, but remains independently testable through metadata generation.
- **User Story 3 (Phase 5)**: Depends on Foundational; can run in parallel with US2 after Piper backend boundaries exist.
- **Polish (Phase 6)**: Depends on selected user stories being complete.

### User Story Dependencies

- **US1 Generate test audio from demo text**: MVP; no dependency on US2 or US3.
- **US2 Preserve reproducible benchmark artifacts**: Uses the Piper backend from US1 but validates metadata independently.
- **US3 Handle unavailable synthesis resources clearly**: Uses the Piper backend boundary from US1 and can be implemented alongside US2.

### Parallel Opportunities

- T002 and T003 can run in parallel.
- T004 and T005 can run in parallel before T006-T009.
- T010, T011, and T012 can run in parallel.
- T019, T020, and T021 can run in parallel.
- T027, T028, T029, T030, and T031 can run in parallel.
- T037, T038, and T039 can run in parallel.

---

## Parallel Example: User Story 1

```text
Task: "T010 [P] [US1] Add failing Piper synthesizer WAV/metadata test with mocked Piper voice in tests/unit/test_tts_synth.py"
Task: "T011 [P] [US1] Add failing notebook helper test for default Piper settings and configured voice discovery in tests/integration/test_pipeline_a_model_adapter.py"
Task: "T012 [P] [US1] Add failing CLI contract test for --engine piper, --voice, --voice-model-path, and --voice-config-path in tests/integration/test_synthesize_audio_cli.py"
```

## Parallel Example: User Story 2

```text
Task: "T019 [P] [US2] Add failing metadata round-trip test for Piper synthesis settings and voice fields in tests/unit/test_audio_metadata.py"
Task: "T020 [P] [US2] Add failing deterministic repeated-generation test for Piper metadata in tests/unit/test_tts_synth.py"
Task: "T021 [P] [US2] Add failing integration test that audio.jsonl is written only after all records are synthesized in tests/integration/test_synthesize_audio_cli.py"
```

## Parallel Example: User Story 3

```text
Task: "T027 [P] [US3] Add failing missing piper-tts dependency test in tests/unit/test_tts_synth.py"
Task: "T028 [P] [US3] Add failing missing voice model/config validation test in tests/unit/test_tts_synth.py"
Task: "T029 [P] [US3] Add failing CLI failure test that no audio.jsonl is written for incomplete Piper runs in tests/integration/test_synthesize_audio_cli.py"
Task: "T030 [P] [US3] Add failing validation tests for empty text, blank text, and duplicate audio paths in tests/unit/test_tts_synth.py"
Task: "T031 [P] [US3] Add failing CLI test for existing output collision behavior in tests/integration/test_synthesize_audio_cli.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup.
2. Complete Phase 2 foundational backend settings, selection, and default voice discovery.
3. Complete Phase 3 User Story 1.
4. Validate with mocked Piper tests and notebook helper compatibility.
5. Stop and demo `demo.synthesize_demo_audio(...)` using configured Piper resources.

### Incremental Delivery

1. Add Piper generation path for the existing helper and CLI.
2. Add reproducible metadata and manifest guarantees.
3. Add hardened resource, validation, collision, and partial-failure behavior.
4. Run full quality checks and bounded fixture smoke command.

### Notes

- [P] tasks modify different files or can be prepared without depending on incomplete implementation.
- Tests should be written first and fail before implementation.
- Keep real Piper voice files and generated audio outside Git.
- Do not add model adapter, metrics, parser repair, or tool schema work unless a task explicitly calls for it.
