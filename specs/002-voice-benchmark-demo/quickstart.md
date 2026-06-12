# Quickstart: Bilingual Voice Benchmark Demo

## Prerequisites

- Python 3.11+
- `uv` for dependency management
- No cloud service, paid API, GPU, or real model download is required for MVP smoke validation

## Install

```powershell
make install
```

or directly:

```powershell
uv sync --all-groups
```

## Generate The Dataset

```powershell
uv run python scripts/generate_dataset.py --version v1 --output data/generated/v1/examples.jsonl
```

Expected result:

- 240 JSONL text examples at `data/generated/v1/examples.jsonl`
- 120 Russian and 120 English examples
- 15% no-tool examples overall and per language
- deterministic 70/15/15 train/validation/test split
- expected `needs_tool`, `expected_tool_call`, and `expected_final_answer` fields

## Synthesize Audio

```powershell
uv run python scripts/synthesize_audio.py --dataset data/generated/v1/examples.jsonl --output data/generated/v1/audio
```

Expected result:

- one deterministic audio fixture per text example under `data/generated/v1/audio/`
- audio metadata JSONL at `data/generated/v1/audio/audio.jsonl` linking `audio_id` to `example_id`
- synthesis settings recorded for reproducibility

## Run Deterministic Smoke Benchmark

Pipeline A consumes the text dataset; pipelines B, C, and D consume the audio
metadata JSONL. Run each pipeline with the mock adapter:

```powershell
uv run python scripts/run_benchmark.py --pipeline A --dataset data/generated/v1/examples.jsonl --run-id smoke --model mock --output runs/smoke/pipeline-a.jsonl
uv run python scripts/run_benchmark.py --pipeline B --audio-metadata data/generated/v1/audio/audio.jsonl --run-id smoke --model mock --output runs/smoke/pipeline-b.jsonl
uv run python scripts/run_benchmark.py --pipeline C --audio-metadata data/generated/v1/audio/audio.jsonl --run-id smoke --model mock --output runs/smoke/pipeline-c.jsonl
uv run python scripts/run_benchmark.py --pipeline D --audio-metadata data/generated/v1/audio/audio.jsonl --run-id smoke --model mock --output runs/smoke/pipeline-d.jsonl
```

Add `--limit 30` to any command for a faster bounded run.

Expected result:

- one `PipelineRun` JSONL artifact per pipeline under `runs/smoke/`
- raw model outputs saved for every example
- parsed envelopes saved when valid
- validation errors saved when invalid
- repair attempts and repair success recorded
- registered tool manifests built for prompts and validation
- optional tool execution results recorded only through `ToolRegistry` and `ToolExecutor`
- structured failures recorded for unknown tools, invalid arguments, and execution errors

## Build Report

```powershell
uv run python scripts/build_report.py --dataset data/generated/v1/examples.jsonl --run runs/smoke/pipeline-a.jsonl --run runs/smoke/pipeline-b.jsonl --run runs/smoke/pipeline-c.jsonl --run runs/smoke/pipeline-d.jsonl --output reports/smoke-report.md --summary reports/smoke-summary.csv --plots-dir reports/plots
```

Expected result:

- markdown report at `reports/smoke-report.md`
- per-pipeline metrics summary at `reports/smoke-summary.csv` (use a `.parquet` suffix for Parquet)
- plot images under `reports/plots/`

Expected report contents:

- dataset summary
- per-pipeline metrics
- Russian and English metric splits
- tool/no-tool confusion matrix
- WER for audio transcript paths
- modality-gap comparison
- best-pipeline rationale
- categorized failure cases

## Run Tests

```powershell
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
```

Required coverage areas:

- `ToolProvider`, `ToolRegistry`, and `ToolExecutor` behavior
- registry-backed tool manifest builder behavior
- `units.convert` provider schema validation and executor behavior
- JSON parsing and single repair attempt
- dataset generation, balancing, and splits
- TTS metadata generation
- WER normalization and calculation
- tool-use metrics and partial-call diagnostics
- pipeline orchestration for A-D with `MockModelAdapter`

## Optional Demo API

```powershell
uv run python -m apps.api
```

The optional API is for local demo execution only. The MVP does not require a complex UI.

## Demo Notebook

Open `apps/notebook/voice_benchmark_demo.ipynb`. It runs against the committed
fixture dataset out of the box (or `data/generated/v1/` when generated) and
demonstrates Russian and English text examples, audio transcript output, audio
tool calling, optional execution, metrics, and the final report. Notebook
artifacts are written under `runs/notebook/` and stay outside Git.

## PR Evidence

Include:

- linked Speckit task IDs
- ruff output
- mypy output
- pytest output
- deterministic smoke benchmark command and artifact path
- generated report path or summary

See `specs/002-voice-benchmark-demo/validation.md` for recorded evidence.
