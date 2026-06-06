# Implementation Plan: Bilingual Voice Benchmark Demo

**Branch**: `004-voice-benchmark-demo` | **Date**: 2026-06-06 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-voice-benchmark-demo/spec.md`

## Summary

Build a Python 3.11+ benchmark and demo system for Russian/English voice assistant tool use. The system generates a balanced JSONL dataset with synthesized audio, runs four text/audio pipelines, parses and validates model JSON envelopes for `units.convert`, optionally executes validated conversions, records all raw and parsed artifacts, computes ASR and tool-use metrics, and produces a final markdown report plus a demo notebook. The MVP avoids weather, cloud-service requirements, and complex UI work.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: pydantic, jsonschema, jiwer, pandas, pytest, ruff, matplotlib, FastAPI for the optional demo backend

**Storage**: Local filesystem artifacts. JSONL is the primary dataset and per-example run format; Parquet or CSV is used for metrics summaries; markdown is used for final reports; generated audio and benchmark outputs stay outside Git except small fixtures.

**Testing**: pytest for unit, integration, and smoke/e2e tests; ruff for linting and formatting checks

**Target Platform**: Local developer machines and CI runners without required GPU, cloud services, paid APIs, or large model downloads for MVP validation

**Project Type**: Python monorepo with reusable packages, CLI app, optional API app, and notebook demo

**Performance Goals**: Bounded smoke benchmark completes on a normal CI runner with deterministic mock adapters; full model/audio experiments may run manually outside ordinary CI.

**Constraints**: Model tool-decision outputs use the canonical JSON envelope; invalid first-pass JSON gets one retry/repair attempt; first-pass parsability remains distinct from repaired success; validated `units.convert` calls are the only executable MVP tool calls; generated datasets, audio, run outputs, checkpoints, and reports are not committed.

**Scale/Scope**: 240 synthetic text examples, 120 Russian and 120 English, 15% no-tool overall and per language, deterministic 70/15/15 split stratified by language, tool/no-tool label, and unit family; every text example has a synthesized audio counterpart.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Benchmark-first**: PASS. Required metrics are defined before implementation and mapped to `packages/metrics`, `packages/asr_eval`, and `packages/report_builder`.
- **Tool validation**: PASS. `packages/tool_schema` owns Pydantic models, JSON Schema, validation errors, and deterministic `units.convert` execution; pipelines cannot execute a tool until validation succeeds.
- **JSON outputs**: PASS. Raw outputs, first-pass parse status, repair attempts, parsed envelopes, and validation errors are saved for every model-output example.
- **Dataset discipline**: PASS. Dataset versioning, deterministic stratified splits, JSONL format, and generation metadata are planned.
- **Modality parity**: PASS. Text and audio examples share stable IDs and split assignment for modality-gap computation.
- **Tool scope**: PASS. `units.convert` is the only MVP tool; weather is explicitly excluded from datasets, prompts, schemas, pipelines, tests, and reports.
- **Experiment artifacts**: PASS. Runs save inputs, raw outputs, parsed outputs, validation errors, repair attempts, execution results, answers, per-example metrics, and aggregate summaries.
- **Modular boundary**: PASS. Package boundaries are fixed for tool schema, dataset builder, TTS, model runner, pipeline runner, ASR eval, metrics, and report builder.
- **Required tests**: PASS. Plan includes tests for schema validation, parser repair, metrics, ASR normalization/WER, dataset generation, and pipeline orchestration.
- **CI coverage**: PASS. PR CI will run ruff checks, pytest, and a deterministic smoke benchmark using `MockModelAdapter`.
- **Full benchmarks**: PASS. Gemma3n and real ASR/model runs are manual experiments and do not block normal CI.
- **Git hygiene**: PASS. Large generated artifacts are ignored; CI/full-run outputs are retained as external workflow or local artifacts rather than committed.
- **PR evidence**: PASS. PR evidence will include task IDs, ruff/pytest output, smoke benchmark metrics, and relevant generated report paths.

## Project Structure

### Documentation (this feature)

```text
specs/002-voice-benchmark-demo/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── api.md
│   ├── artifacts.md
│   ├── cli.md
│   └── model-output.schema.json
├── checklists/
│   ├── benchmark-coverage.md
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/
├── api/                 # Optional FastAPI demo backend
├── cli/                 # Command-line dataset, pipeline, benchmark, and report entrypoints
└── notebook/            # Final demonstration notebook

packages/
├── tool_schema/         # Pydantic models, JSON Schema validation, parser repair, units.convert executor
├── dataset_builder/     # Synthetic JSONL text dataset generation and deterministic splits
├── tts_synth/           # Audio synthesis adapters, metadata, and fixture generation
├── model_runner/        # Gemma3nAdapter, ASRAdapter, TextLLMAdapter, MockModelAdapter
├── pipeline_runner/     # Pipelines A-D orchestration and artifact writing
├── asr_eval/            # Transcript normalization and WER calculation
├── metrics/             # Tool-use metrics, confusion matrix, modality gap, aggregations
└── report_builder/      # Markdown report, tables, and matplotlib plots

configs/
├── prompts/             # Prompt templates for pipelines A-D
├── tools/               # Tool schema/config exports
├── models/              # Adapter configuration examples
└── experiments/         # Benchmark run configuration examples

data/
├── fixtures/            # Small deterministic examples and tiny audio fixtures only
├── raw/.gitkeep
└── processed/.gitkeep

reports/
└── .gitkeep

scripts/
├── generate_dataset.py
├── synthesize_audio.py
├── run_benchmark.py
└── build_report.py

tests/
├── unit/
├── integration/
└── e2e/
```

**Structure Decision**: Use the exact monorepo layout above. Packages isolate benchmark responsibilities, apps provide user-facing execution surfaces, configs hold prompts and experiment settings, and generated artifacts remain outside tracked source except bounded fixtures and `.gitkeep` files.

## Complexity Tracking

No constitution violations are planned.

## Phase 0 Research Summary

See [research.md](research.md). Decisions resolve dataset format, metrics summary format, schema validation stack, ASR/WER tooling, plotting scope, adapter boundaries, and MVP exclusions.

## Phase 1 Design Summary

See [data-model.md](data-model.md), [quickstart.md](quickstart.md), and [contracts/](contracts/). Contracts define CLI commands, optional demo API behavior, artifact formats, and the canonical model-output JSON Schema.

## Post-Design Constitution Check

- **Benchmark-first**: PASS. Quickstart defines dataset, smoke benchmark, audio metrics, and report commands.
- **Tool validation**: PASS. Contracts require schema validation before optional execution.
- **JSON outputs**: PASS. Artifact contract preserves raw output, parse status, repair status, parsed envelope, and validation errors.
- **Dataset discipline**: PASS. Data model records version, generation settings, and deterministic split metadata.
- **Modality parity**: PASS. Data model requires shared `example_id` for text/audio pairs.
- **Tool scope**: PASS. Contracts only expose `units.convert`.
- **Experiment artifacts**: PASS. Artifact contract covers per-example JSONL, metrics summaries, report markdown, and plots.
- **Modular boundary**: PASS. Package responsibilities are named in Project Structure.
- **Required tests**: PASS. Quickstart and contracts identify schema, repair, metrics, WER, dataset, and pipeline smoke tests.
- **CI coverage**: PASS. Smoke path uses `MockModelAdapter`.
- **Full benchmarks**: PASS. Real model/audio-capable adapter experiments are manual.
- **Git hygiene**: PASS. Generated artifacts are local or workflow artifacts, not committed.
- **PR evidence**: PASS. Quickstart lists validation evidence expected for PR review.
