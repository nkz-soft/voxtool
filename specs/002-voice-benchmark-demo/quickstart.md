# Quickstart: Bilingual Voice Benchmark Demo

## Prerequisites

- Python 3.11+
- Local development environment with project dependencies installed
- No cloud service, paid API, GPU, or real model download is required for MVP smoke validation

## Install

```powershell
python -m pip install -e ".[dev]"
```

## Generate The Dataset

```powershell
python scripts/generate_dataset.py --version v1 --output data/generated/v1/examples.jsonl
```

Expected result:

- 240 JSONL text examples
- 120 Russian and 120 English examples
- 15% no-tool examples overall and per language
- deterministic 70/15/15 train/validation/test split
- expected `needs_tool`, `tool_call`, and `final_answer` fields

## Synthesize Audio

```powershell
python scripts/synthesize_audio.py --dataset data/generated/v1/examples.jsonl --output data/generated/v1/audio
```

Expected result:

- one audio artifact per text example
- audio metadata JSONL linking `audio_id` to `example_id`
- synthesis settings recorded for reproducibility

## Run Deterministic Smoke Benchmark

```powershell
python scripts/run_benchmark.py --dataset data/generated/v1/examples.jsonl --adapter mock --pipelines A,B,C,D --output runs/smoke
```

Expected result:

- raw model outputs saved for every example
- parsed envelopes saved when valid
- validation errors saved when invalid
- repair attempts and repair success recorded
- registered tool manifests built for prompts and validation
- optional tool execution results recorded only through `ToolRegistry` and `ToolExecutor`
- structured failures recorded for unknown tools, invalid arguments, and execution errors
- per-pipeline metrics summaries written as CSV or Parquet

## Build Report

```powershell
python scripts/build_report.py --runs runs/smoke --output reports/smoke-report.md
```

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
python -m pytest
python -m ruff check .
python -m ruff format --check .
python -m mypy
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
python -m apps.api
```

The optional API is for local demo execution only. The MVP does not require a complex UI.

## Demo Notebook

Open the notebook under `apps/notebook/` after generating a dataset and at least one benchmark run. It should demonstrate Russian and English examples for text input, audio transcript output, audio tool calling, optional execution, and final answer display.

## PR Evidence

Include:

- linked Speckit task IDs
- ruff output
- mypy output
- pytest output
- deterministic smoke benchmark command and artifact path
- generated report path or summary
