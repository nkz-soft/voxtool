# VoxTool

[![CI](https://github.com/nkz-soft/voxtool/actions/workflows/ci.yml/badge.svg)](https://github.com/nkz-soft/voxtool/actions/workflows/ci.yml)
[![Benchmark Smoke](https://github.com/nkz-soft/voxtool/actions/workflows/benchmark-smoke.yml/badge.svg)](https://github.com/nkz-soft/voxtool/actions/workflows/benchmark-smoke.yml)

VoxTool is a multilingual voice assistant benchmark and demo scaffold. The MVP
focuses on reproducible text/audio tool-use evaluation for `units.convert` with
English and Russian examples, deterministic smoke runs, strict JSON/tool schema
validation boundaries, and generated artifacts kept outside Git.

## MVP Scope

- 240 synthetic text examples: 120 Russian and 120 English, 15% no-tool
  overall and per language, deterministic 70/15/15 train/validation/test split
- one deterministic synthesized audio counterpart per text example
- four benchmark pipelines: A (text), B (audio ASR transcript), C (direct
  audio tool use), and D (ASR transcript then text LLM)
- canonical JSON envelope outputs with first-pass parse status, one
  repair attempt, and recorded validation errors
- `units.convert` as the required initial tool provider; all tool calls are
  resolved through `ToolRegistry` and executed through `ToolExecutor`
- ASR WER, tool-use metrics, tool/no-tool confusion matrix, modality gap,
  and a final markdown report with plots
- deterministic `MockModelAdapter` smoke runs that work on a normal CI runner

## Non-Goals

- no weather tool anywhere: datasets, prompts, schemas, pipelines, tests, or
  reports
- no cloud services, paid APIs, GPUs, or large model downloads for MVP
  validation
- no complex UI; the optional FastAPI app is a local demo surface only
- no committed generated artifacts: datasets, audio, runs, checkpoints, and
  reports stay outside Git
- full Gemma3n and real ASR/model experiments are manual and do not block
  ordinary CI

## Quickstart

```bash
make install
uv run python scripts/generate_dataset.py --version v1 --output data/generated/v1/examples.jsonl
uv run python scripts/synthesize_audio.py --dataset data/generated/v1/examples.jsonl --output data/generated/v1/audio
uv run python scripts/run_benchmark.py --pipeline A --dataset data/generated/v1/examples.jsonl --run-id smoke --model mock --output runs/smoke/pipeline-a.jsonl
uv run python scripts/run_benchmark.py --pipeline B --audio-metadata data/generated/v1/audio/audio.jsonl --run-id smoke --model mock --output runs/smoke/pipeline-b.jsonl
uv run python scripts/run_benchmark.py --pipeline C --audio-metadata data/generated/v1/audio/audio.jsonl --run-id smoke --model mock --output runs/smoke/pipeline-c.jsonl
uv run python scripts/run_benchmark.py --pipeline D --audio-metadata data/generated/v1/audio/audio.jsonl --run-id smoke --model mock --output runs/smoke/pipeline-d.jsonl
uv run python scripts/build_report.py --dataset data/generated/v1/examples.jsonl --run runs/smoke/pipeline-a.jsonl --run runs/smoke/pipeline-b.jsonl --run runs/smoke/pipeline-c.jsonl --run runs/smoke/pipeline-d.jsonl --output reports/smoke-report.md --summary reports/smoke-summary.csv --plots-dir reports/plots
```

The demo notebook at `apps/notebook/voice_benchmark_demo.ipynb` runs the same
flow against the committed fixture dataset with mock adapters. See
[specs/002-voice-benchmark-demo/quickstart.md](specs/002-voice-benchmark-demo/quickstart.md)
for the full quickstart with expected artifacts.

## Fresh Clone Setup

```bash
make install
make lint
make typecheck
make test
```

The project uses Python 3.11+ and `uv` for dependency management.

## Developer Commands

```bash
make install
make lint
make typecheck
make test
make benchmark-smoke
```

`make benchmark-smoke` runs the deterministic MockModelAdapter smoke command
with a 30-example limit and writes artifacts under `reports/smoke`.

## GitHub Workflows

- `ci.yml` runs on pushes and pull requests to `main` and `develop`, executing
  ruff check, ruff format check, mypy, pytest, and coverage artifact upload.
- `benchmark-smoke.yml` runs on pull requests and manual dispatch without GPU,
  paid APIs, real model downloads, or large audio generation.
- `report.yml` is manual-only and accepts model and limit inputs for full report
  runs with 90-day artifact retention.
- `release.yml` runs on `v*.*.*` tags and uploads release report artifacts.

Pull requests should include Spec Kit task IDs plus validation evidence for CI,
smoke benchmark results, artifacts, and any known deviations.

Public package interfaces, CLI commands, API routes, notebook helpers, and
benchmark-critical functions or methods must include concise descriptions of
their purpose, important inputs or outputs, and non-obvious failure behavior.

## Artifact Policy

Generated audio, evaluation results, benchmark reports, model files,
checkpoints, `wandb`, `mlruns`, and large datasets must not be committed. Keep
generated outputs in ignored artifact directories and upload CI/report outputs
as GitHub Actions artifacts with the configured retention period.
