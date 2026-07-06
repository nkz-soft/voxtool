# Implementation Plan: Piper Audio Dataset

**Branch**: `004-piper-audio-dataset` | **Date**: 2026-07-05 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/004-piper-audio-dataset/spec.md`

## Summary

Extend the existing benchmark input TTS package so the notebook helper can
generate real Piper TTS WAV samples from the labeled bilingual text dataset with
the existing high-level call, while preserving the metadata contract, split
alignment, and fixture-only CI path. Piper is the user-facing demo synthesis
mode; fixture-silent remains an explicit bounded mode for tests and CI.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Existing stack remains pydantic, typer, pytest, ruff,
mypy, and JSONL helpers. Piper is provided by the optional `speech` dependency
group through `piper-tts`; real voices are local `.onnx` plus `.onnx.json`
artifacts and are not committed.

**Storage**: Local filesystem artifacts. Generated WAV files and full audio
metadata are local outputs under caller-selected directories such as
`demo_audio/`; small fixtures and contract docs stay in Git.

**Testing**: pytest for unit and integration tests, with mocks or tiny fixture
writers for CI. Real Piper synthesis is validated manually or in an opt-in
workflow with installed speech dependencies and downloaded voices.

**Target Platform**: Local developer machines, Google Colab/manual notebooks,
and ordinary CI runners for import-safe mock/fixture validation.

**Project Type**: Python monorepo with reusable packages, Typer CLI, scripts,
notebook helpers, JSONL dataset artifacts, and tests.

**Performance Goals**: Bounded demo dataset synthesis completes interactively
for notebook users. Ordinary CI remains lightweight and does not download Piper
voices or synthesize full real-audio datasets.

**Constraints**: The current high-level notebook call remains valid and uses
Piper for demo audio generation. Piper mode must not silently fall back to
fixture-silent audio. Audio records must
preserve source example IDs, dataset version, language, split, transcript, path,
engine, voice, sample rate, and duration when known. Generated audio and voice
models stay out of Git.

**Scale/Scope**: Bounded bilingual demo datasets first; full benchmark audio
sets are manual artifacts. This feature affects benchmark input TTS, not model
adapters, JSON output parsing, tool schemas, or metrics formulas.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Benchmark-first**: PASS. Success is tied to reproducible audio metadata,
  bounded smoke validation, and manual real-audio artifact evidence.
- **Tool validation**: PASS. No tool schemas or tool execution behavior change;
  source example tool labels are preserved.
- **JSON outputs**: PASS. Model JSON output handling is unchanged; downstream
  audio pipeline artifacts keep existing raw/parsed/error behavior.
- **Dataset discipline**: PASS. Audio examples inherit source dataset version
  and deterministic split membership.
- **Modality parity**: PASS. Text and audio share semantic source example IDs.
- **Tool scope**: PASS. Existing benchmark tool labels remain explicit and
  weather is not introduced.
- **Experiment artifacts**: PASS. Plan saves audio metadata, synthesis settings,
  source links, and manual artifact paths while leaving generated audio local.
- **Modular boundary**: PASS. Changes stay in `packages/tts_synth`, `apps/cli`,
  `apps/notebook`, `scripts`, tests, and related docs.
- **Required tests**: PASS. No parser repair, metrics, or schema-validation
  changes are planned; pipeline compatibility gets bounded integration coverage.
- **Public API documentation**: PASS. New/changed public synthesizers, settings,
  CLI options, scripts, and notebook helpers require concise descriptions.
- **CI coverage**: PASS. PR validation remains lint, format check, typecheck,
  tests, and smoke benchmark without large downloads.
- **Full benchmarks**: PASS. Real Piper generation and model evaluation are
  manual or suitable workflow artifacts.
- **Git hygiene**: PASS. `.gitignore` already excludes generated audio, ONNX
  voice models, and generated benchmark outputs.
- **PR evidence**: PASS. PR should link tasks from this feature and include CI
  output plus a manual Piper synthesis artifact path when available.

## Project Structure

### Documentation (this feature)

```text
specs/004-piper-audio-dataset/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── audio-cli.md
│   ├── notebook-helper.md
│   └── audio-metadata.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/
├── cli/
│   └── audio.py                  # audio synthesis command options
└── notebook/
    └── colab_demo_helpers.py     # synthesize_demo_audio helper

packages/
└── tts_synth/
    ├── __init__.py               # public exports
    ├── io.py                     # audio metadata JSONL helpers
    ├── models.py                 # SynthesisSettings and AudioExample
    └── synthesizer.py            # fixture and Piper synthesis backends

scripts/
└── synthesize_audio.py           # direct CLI script entrypoint

tests/
├── unit/
│   ├── test_audio_metadata.py
│   └── test_tts_synth.py
├── integration/
│   ├── test_synthesize_audio_cli.py
│   └── test_pipeline_a_model_adapter.py
└── e2e/
    └── test_colab_demo_notebook.py
```

**Structure Decision**: Extend the existing `tts_synth` package rather than add
a separate speech-output package, because this feature creates benchmark input
audio from text examples. Keep model-output speech synthesis out of scope.

## Complexity Tracking

No constitution violations are planned.

## Phase 0 Research Summary

See [research.md](research.md). Decisions cover the Piper integration surface,
voice artifact handling, CI boundaries, bilingual voice selection, output
atomicity, and metadata compatibility.

## Phase 1 Design Summary

See [data-model.md](data-model.md), [quickstart.md](quickstart.md), and
[contracts/](contracts/). Contracts define the notebook helper behavior, CLI
options, and audio metadata compatibility expectations.

## Post-Design Constitution Check

- **Benchmark-first**: PASS. Quickstart defines CI validation and manual Piper
  synthesis evidence.
- **Tool validation**: PASS. Tool registry behavior is unaffected.
- **JSON outputs**: PASS. Model JSON output artifacts remain unchanged.
- **Dataset discipline**: PASS. Data model requires source version and split
  inheritance for every audio record.
- **Modality parity**: PASS. Contracts require source example alignment.
- **Tool scope**: PASS. No weather or new benchmark tools are introduced.
- **Experiment artifacts**: PASS. Metadata and run status are saved; large
  audio/model artifacts stay local or workflow-retained.
- **Modular boundary**: PASS. Plan scopes changes to TTS input generation,
  notebook helper, CLI/script, and tests.
- **Required tests**: PASS. Tests cover metadata, backend selection, missing
  resource failure, CLI behavior, and notebook helper compatibility.
- **Public API documentation**: PASS. Public functions/classes/options are
  listed as documentation tasks for implementation.
- **CI coverage**: PASS. Ordinary CI remains mock/fixture-based.
- **Full benchmarks**: PASS. Real Piper synthesis is manual or opt-in workflow.
- **Git hygiene**: PASS. Generated WAV/ONNX artifacts remain ignored.
- **PR evidence**: PASS. PR evidence is specified in quickstart and future
  tasks should reference this feature.
