# VoxTool

[![CI](https://github.com/nickspring/voxtool/actions/workflows/ci.yml/badge.svg)](https://github.com/nickspring/voxtool/actions/workflows/ci.yml)
[![Benchmark Smoke](https://github.com/nickspring/voxtool/actions/workflows/benchmark-smoke.yml/badge.svg)](https://github.com/nickspring/voxtool/actions/workflows/benchmark-smoke.yml)

VoxTool is a multilingual voice assistant benchmark and demo scaffold. The MVP
focuses on reproducible text/audio tool-use evaluation for `units.convert` with
English and Russian examples, deterministic smoke runs, strict JSON/tool schema
validation boundaries, and generated artifacts kept outside Git.

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

## Artifact Policy

Generated audio, evaluation results, benchmark reports, model files,
checkpoints, `wandb`, `mlruns`, and large datasets must not be committed. Keep
generated outputs in ignored artifact directories and upload CI/report outputs
as GitHub Actions artifacts with the configured retention period.
