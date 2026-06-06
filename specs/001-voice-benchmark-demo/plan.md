# Implementation Plan: Multilingual Voice Benchmark Demo

**Branch**: `001-voice-benchmark-planning` | **Date**: 2026-06-06 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-voice-benchmark-demo/spec.md`

## Summary

Build a Python 3.11+ monorepo for a multilingual voice assistant benchmark and
demo system. The system accepts text or audio, evaluates whether a tool is
required, validates structured JSON tool invocations for `units.convert`,
optionally executes validated calls, and compares four text/audio pipelines with
saved artifacts and reproducible metrics.

The implementation uses `uv` for environment and dependency management, modular
packages for the benchmark components, Typer for CLI workflows, optional FastAPI
for demo backend execution, GitHub Actions for CI/smoke/report/release
automation, and strict generated-artifact exclusion from Git.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: uv, Pydantic, Typer, FastAPI, pytest, ruff, mypy,
coverage.py, PyYAML, pandas, jiwer

**Storage**: Local filesystem paths for configs, small fixtures, generated
artifact directories, and workflow artifacts; generated datasets/audio/results
are excluded from Git

**Testing**: pytest for unit, integration, and e2e tests; ruff check; ruff
format --check; mypy; coverage.xml upload in CI

**Target Platform**: Local developer machines and GitHub Actions hosted runners
for PR CI; manual full benchmarks may use self-hosted GPU runners

**Project Type**: Python monorepo with CLI app, optional API app, notebooks,
benchmark packages, scripts, and GitHub automation

**Performance Goals**: PR smoke benchmark completes in under 5 minutes on a
standard hosted runner with about 30 deterministic examples; normal PR CI avoids
GPU, paid APIs, real model downloads, and large audio generation

**Constraints**: All tool calls validate against schema before execution; model
outputs are JSON or logged failures; generated audio, evaluation results,
reports, model files, checkpoints, wandb, mlruns, and large datasets are not
committed; PR artifacts retained 14 days; manual full benchmark/release report
artifacts retained 90 days

**Scale/Scope**: MVP benchmark covers `units.convert`, Russian and English
examples, four pipelines A-D, MockModelAdapter smoke benchmark with about 30
examples, and manually triggered full reports

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Benchmark-first**: PASS. Smoke benchmark and full benchmark/report workflows
  are planned before implementation. Metrics are defined in `research.md` and
  `data-model.md`.
- **Tool validation**: PASS. `packages/tool_schema` owns Pydantic models, JSON
  Schema validation, and `units.convert` execution; all pipelines validate
  before optional execution.
- **JSON outputs**: PASS. Model adapter outputs are parsed as JSON; invalid JSON
  is a failed result saved with raw output and validation details.
- **Dataset discipline**: PASS. `packages/dataset_builder` owns dataset versions
  and deterministic train/validation/test splits.
- **Modality parity**: PASS. Dataset examples use shared semantic IDs across
  text and audio variants to measure modality gap.
- **Tool scope**: PASS. MVP tool scope is `units.convert`; weather is not
  required by datasets, prompts, schemas, pipelines, tests, or reports.
- **Experiment artifacts**: PASS. Pipeline runs save inputs, raw outputs, parsed
  outputs, validation errors, metrics, and report artifacts outside Git.
- **Modular boundary**: PASS. Packages are separated for dataset generation,
  TTS, model runner, pipeline runner, tools, metrics, and reports.
- **Required tests**: PASS. Plan includes schema validation, parser repair,
  metrics, and pipeline orchestration tests.
- **CI coverage**: PASS. `ci.yml` runs ruff check, ruff format --check, mypy,
  pytest, and uploads `coverage.xml`.
- **Full benchmarks**: PASS. `report.yml` is workflow_dispatch only with model
  and limit inputs; full model/audio work is manual-only.
- **Git hygiene**: PASS. Generated artifacts are ignored and uploaded as limited
  retention workflow artifacts.
- **PR evidence**: PASS. PR template requires Speckit task IDs and validation
  evidence.

## Project Structure

### Documentation (this feature)

```text
specs/001-voice-benchmark-demo/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── api.md
│   ├── cli.md
│   ├── pipeline-artifacts.md
│   └── tool-invocation.schema.json
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
apps/
├── api/                 # Optional FastAPI demo backend
├── cli/                 # Typer CLI entrypoints
└── notebook/            # Demo and final report notebooks

packages/
├── tool_schema/         # Pydantic models, JSON Schema validation, units.convert
├── dataset_builder/     # Synthetic RU/EN dataset generation and splits
├── tts_synth/           # Audio synthesis interfaces and fixture generation
├── model_runner/        # Model adapters, including MockModelAdapter
├── pipeline_runner/     # Pipelines A-D orchestration
├── metrics/             # Tool-use, ASR, and modality gap metrics
└── report_builder/      # Markdown reports and tables

configs/
├── tools/
├── prompts/
├── models/
└── experiments/

data/
├── raw/.gitkeep
├── processed/.gitkeep
└── fixtures/

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

.github/
├── workflows/
│   ├── ci.yml
│   ├── benchmark-smoke.yml
│   ├── report.yml
│   └── release.yml
├── ISSUE_TEMPLATE/
├── pull_request_template.md
└── dependabot.yml
```

**Structure Decision**: Use the exact monorepo structure above. Top-level
folders match the specification, while fixed `packages/` boundaries enforce the
constitution's modularity requirement and keep benchmark logic reusable by CLI,
API, scripts, notebooks, and tests.

## Complexity Tracking

No constitution violations are planned.
