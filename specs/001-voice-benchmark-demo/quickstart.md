# Quickstart: Multilingual Voice Benchmark Demo

## Prerequisites

- Python 3.11+
- uv
- make

## Fresh Clone Validation

```bash
make install
make lint
make typecheck
make test
```

## Generate a Small Dataset

```bash
uv run python scripts/generate_dataset.py \
  --config configs/experiments/smoke.yml \
  --output data/processed/smoke
```

Generated dataset outputs stay out of Git unless they are intentionally small
test fixtures.

## Synthesize Audio Fixtures

```bash
uv run python scripts/synthesize_audio.py \
  --dataset data/processed/smoke \
  --output data/processed/audio-smoke
```

Large generated audio stays out of Git. Commit only small bounded fixtures that
are required for deterministic tests.

## Run Smoke Benchmark

```bash
uv run python scripts/run_benchmark.py \
  --config configs/experiments/smoke.yml \
  --model mock \
  --limit 30 \
  --output reports/smoke
```

The smoke benchmark uses MockModelAdapter, runs all four pipelines, includes
English and Russian examples, covers tool-required/no-tool cases, invalid
JSON/schema cases, and writes metrics/artifacts.

## Build Report

```bash
uv run python scripts/build_report.py \
  --input reports/smoke \
  --output reports/smoke-report.md
```

Full report generation is manual-only and should be run through `report.yml` or
an equivalent local command when model/audio resources are available.

## Optional Demo API

```bash
uv run fastapi dev apps/api/main.py
```

The API is for optional demo/backend execution only. It must validate tool
requests before executing `units.convert`.

## CLI Demo

```bash
uv run python -m apps.cli text "convert 2 kilometers to meters"
uv run python -m apps.cli audio path/to/request.wav
```

## GitHub Workflows

- `ci.yml`: push and pull_request to `main` and `develop`; ruff check, ruff
  format --check, mypy, pytest, upload `coverage.xml`.
- `benchmark-smoke.yml`: pull_request and workflow_dispatch; MockModelAdapter,
  about 30 examples, upload smoke artifacts for 14 days.
- `report.yml`: workflow_dispatch only; accepts `model` and `limit` inputs;
  uploads full report artifacts for 90 days.
- `release.yml`: `v*.*.*` tags; attaches smoke report artifacts; release
  publishing is manual-only.
- `dependabot.yml`: weekly updates for GitHub Actions and Python dependencies.
