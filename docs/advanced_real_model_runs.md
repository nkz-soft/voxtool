# Advanced Real-Model and GPU Workflows

This document describes the **manual** workflows for running real model adapters
(Voxtral, Qwen, Gemma). Ordinary CI never downloads models or requires a GPU —
it validates adapters with import, config, and contract tests only. Real runs
happen locally on a capable machine, in Google Colab, or on a GPU runner via the
`workflow_dispatch` workflow.

## Adapters and configs

| Adapter ID | Config | Pipelines | Notes |
|------------|--------|-----------|-------|
| `voxtral`  | `configs/models/voxtral.yaml` | A, C, D | Audio + text; emits transcript. |
| `qwen`     | `configs/models/qwen.yaml`    | A, D    | Text-only; supports LoRA + quantization. |
| `gemma`    | `configs/models/gemma.yaml`   | A, D    | Text-only; supports LoRA + quantization. |
| `mock`     | (none)                        | A, D    | Deterministic, no download; used in CI. |

Each config declares the model name and capabilities only. `eager_download` is
`false`; weights are fetched lazily on the first `generate_text` call. Editing a
config to set `eager_download: true` is rejected by the registry.

## Installing the model extras

Real adapters need optional heavy dependencies that are **not** installed in
ordinary CI:

```bash
uv sync --group model   # or: pip install -e '.[model]'
```

## Running a real adapter benchmark

Run Pipeline A (text) with a real adapter using the CLI:

```bash
uv run python -m apps.cli benchmark run \
  --pipeline A \
  --model qwen \
  --dataset data/fixtures/advanced/sample_text.jsonl \
  --output reports/runs/qwen-smoke.jsonl \
  --run-id qwen-smoke \
  --limit 5
```

Or with the script entrypoint:

```bash
uv run python scripts/run_benchmark.py \
  --pipeline A \
  --model gemma \
  --config-path configs/models/gemma.yaml \
  --dataset data/fixtures/advanced/sample_text.jsonl \
  --output reports/runs/gemma-smoke.jsonl \
  --run-id gemma-smoke
```

The selected adapter is built from the registry, capability-checked for the
requested pipeline, and then run through the same parsing, schema validation,
registry tool execution, and artifact logging as the mock path. Each output
record preserves the raw model output, parsed JSON envelope, validation errors,
tool execution result, final answer, and adapter identity/capabilities/profile.

### Capability skips

An adapter that does not declare the capabilities a pipeline requires (for
example, running text-only Qwen on the audio Pipeline C) is rejected **before**
any model executes. The run raises a structured `AdapterPipelineSkip` describing
the missing capabilities, which is recorded distinctly from a model-output
failure.

## Colab demo

`apps/notebook/colab_demo.ipynb` walks through dependency install, repo load,
adapter selection, a text run, optional audio upload, validation, tool
execution, final answers, and metrics. Start with `ADAPTER_ID = 'mock'` for a
no-download dry run, then switch to a real adapter once a GPU runtime is
attached. The notebook helpers live in `apps/notebook/colab_demo_helpers.py`.

## GPU runner workflow

Heavyweight benchmarks use the manual `workflow_dispatch` workflow at
`.github/workflows/gpu-benchmarks.yml`. Trigger it from the GitHub Actions UI or
the CLI:

```bash
gh workflow run gpu-benchmarks.yml
```

Generated artifacts — model caches, full run outputs, and reports — stay outside
Git per the artifact policy in `.gitignore`.
