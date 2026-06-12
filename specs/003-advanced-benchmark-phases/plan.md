# Implementation Plan: Advanced Benchmark Phases

**Branch**: `003-advanced-benchmark-phases` | **Date**: 2026-06-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/003-advanced-benchmark-phases/spec.md`

## Summary

Extend the existing bilingual voice assistant benchmark from deterministic MVP validation into three advanced phases: real Voxtral/Qwen/Gemma model adapters and a Colab demo, LoRA/SFT workflow with a Russian-focused dataset and before/after metrics, and assistant-mode extensions for optional speech output, multiple validated tools, and quantized inference profiles. The implementation keeps the current JSON envelope, registry-first tool execution, JSONL artifacts, deterministic smoke benchmark, and ordinary CI constraints while adding concrete adapter modules, fine-tuning package modules, speech-output package modules, configs, scripts, and notebooks for heavyweight manual workflows.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Existing stack remains pydantic, jsonschema, jiwer, pandas, pytest, ruff, mypy, matplotlib, and optional FastAPI. Advanced manual workflows may add optional extras for Google Colab notebooks, Hugging Face model loading, LoRA/SFT training, quantized inference, and Piper or Edge TTS speech synthesis, but ordinary CI must install only bounded dependencies needed for mocks, fixtures, import/config tests, and contract tests.

**Storage**: Local filesystem artifacts. JSONL remains canonical for datasets, instruction-tuning records, per-example pipeline outputs, and evaluation outputs. CSV or Parquet remains the aggregate metrics format. Notebooks, configs, small fixtures, and contracts are tracked; generated audio, full datasets, run outputs, model checkpoints, adapter caches, and reports remain outside Git.

**Testing**: pytest for unit, integration, smoke, and contract tests; ruff check and format check; mypy for typecheck evidence. Unit tests use `MockModelAdapter` for model behavior. Real adapters have import/config tests only in ordinary CI. Speech output, LoRA, and quantization are tested in CI through mocks, capability declarations, schema checks, and bounded fixtures. Full real-model benchmarks are manual; GPU benchmarks use `workflow_dispatch` or self-hosted runners.

**Target Platform**: Local developer machines, ordinary CI runners without GPU or large downloads, and Google Colab or equivalent manual environments for real-model demo, fine-tuning, speech generation, and quantized inference experiments.

**Project Type**: Python monorepo with reusable packages, CLI app, optional API app, notebook demos, configs, scripts, tests, and generated local artifacts.

**Performance Goals**: Deterministic smoke validation completes on ordinary CI with mocks and fixtures. Colab demo processes a bounded sample dataset interactively. Base-versus-LoRA and base-versus-quantized comparisons run on small evaluation subsets before larger manual experiments.

**Constraints**: Model outputs continue to use the canonical JSON envelope. Invalid first-pass JSON is logged distinctly from repaired success. `ModelAdapter.generate_text(prompt, config) -> ModelResponse` is the common text-generation surface, with `supports_audio_input`, `supports_text_input`, `supports_lora`, and `supports_quantization` capability flags. Tool calls execute only after registry lookup and schema validation. `units.convert`, `text.stress_ru`, and `calculator.simple` are the explicit supported tools; weather remains out of scope. LoRA training, speech output, and quantized inference are optional and disabled in ordinary CI. Large generated artifacts and checkpoints are never committed. Public interfaces and benchmark-critical behaviors require concise descriptions.

**Scale/Scope**: Extends the existing 240-example bilingual benchmark with a new advanced dataset version or compatible extension for Russian adaptation, multi-tool evaluation, speech-output demos, and quantized comparisons. The Colab demo and CI smoke path use small bounded subsets; full real-model and training runs remain manual.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Benchmark-first**: PASS. Required metrics include parsability, tool-decision accuracy, exact tool-call match, exact argument match, false-alarm rate, Russian-only splits, per-tool metrics, speech-output artifact status, and base-vs-adapted/base-vs-quantized deltas.
- **Tool validation**: PASS. Multi-tool execution remains routed through `ToolRegistry` and `ToolExecutor`; unsupported tools and invalid arguments are structured failures and never execute.
- **JSON outputs**: PASS. Raw output, first-pass parse status, repair attempts, parsed envelopes, validation errors, and unsupported-tool failures remain per-example artifacts for every model-output path.
- **Dataset discipline**: PASS. Russian instruction-tuning and multi-tool datasets are versioned and use deterministic train/validation/test splits with labels for language, tool/no-tool, tool name, and scenario category.
- **Modality parity**: PASS. Text and audio paths continue to share semantic examples and split membership where both modalities are evaluated.
- **Tool scope**: PASS. `units.convert` remains the primary tool. `text.stress_ru` and `calculator.simple` are explicit phase additions through the registry; weather remains excluded.
- **Experiment artifacts**: PASS. Plan saves inputs, configs, raw outputs, parsed outputs, validation errors, repair attempts, execution results, final answers, optional speech paths, metrics, and comparison summaries.
- **Modular boundary**: PASS. Changes are mapped to model runner, dataset builder, tool schema, pipeline runner, metrics, report builder, TTS/speech output, notebooks, configs, scripts, and tests.
- **Required tests**: PASS. Plan includes tests for schema validation, parser repair, metrics, registry/tool routing, adapter contracts, dataset splitting, and pipeline orchestration.
- **Public API documentation**: PASS. New adapter classes, tool providers, dataset builders, training/evaluation entrypoints, CLI commands, notebook helpers, and metrics interfaces require concise descriptions.
- **CI coverage**: PASS. PR CI remains lint, format check, typecheck, tests, and deterministic smoke benchmark with mocks or fixtures.
- **Full benchmarks**: PASS. Real-model, audio, LoRA, speech, and quantization runs are manual or suitable-runner workflows and do not block ordinary CI.
- **Git hygiene**: PASS. Generated datasets, audio, checkpoints, model caches, full run outputs, and reports stay outside Git; CI artifacts use limited retention.
- **PR evidence**: PASS. PR evidence must link Spec Kit tasks and include CI output, smoke benchmark output, and relevant manual artifact paths for heavyweight workflows.

## Project Structure

### Documentation (this feature)

```text
specs/003-advanced-benchmark-phases/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── adapters.md
│   ├── artifacts.md
│   ├── cli.md
│   └── tools.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/
├── api/                 # Optional demo API extensions for adapter, speech, and multi-tool responses
├── cli/                 # Commands for adapters, datasets, benchmarks, training/eval, speech, and reports
└── notebook/
    └── colab_demo.ipynb # Colab-ready real-adapter demo

packages/
├── tool_schema/         # ToolDefinition, ToolRegistry, ToolExecutor, ToolSchemaValidator, tool schemas
├── dataset_builder/     # Advanced dataset and instruction-tuning JSONL generation/import/splits
├── finetuning/
│   └── voice_toolbench_finetuning/
│       ├── dataset.py
│       ├── lora_config.py
│       ├── train.py
│       └── evaluate.py
├── speech_output/
│   └── voice_toolbench_speech_output/ # SpeechSynthesizer, Piper/Edge TTS adapters, manifest writer
├── tts_synth/           # Existing benchmark input TTS
├── model_runner/
│   └── voice_toolbench_model_runner/
│       └── adapters/
│           ├── voxtral.py
│           ├── qwen.py
│           └── gemma.py
├── pipeline_runner/     # Pipelines A-D orchestration with real adapters, speech paths, and artifacts
├── asr_eval/            # Existing transcript normalization and WER behavior
├── metrics/             # Russian-only, per-tool, LoRA delta, and quantized comparison metrics
└── report_builder/      # Advanced markdown reports, metrics tables, and comparison plots

configs/
├── prompts/             # Multi-tool and adapter-aware prompt templates
├── tools/               # Registry exports for units.convert, text.stress_ru, calculator.simple
├── models/
│   ├── voxtral.yaml
│   ├── qwen.yaml
│   └── gemma.yaml
├── finetuning/
│   ├── lora_gemma.yaml
│   └── lora_qwen.yaml
├── datasets/
│   ├── ru_units_convert.yaml
│   └── ru_toolbench.yaml
├── inference/
│   ├── full_precision.yaml
│   ├── quantized_8bit.yaml
│   └── quantized_4bit.yaml
├── experiments/         # Colab/demo, LoRA evaluation, speech, and quantized comparison configs
└── training/            # Backward-compatible training config location if already used

data/
├── fixtures/            # Small deterministic datasets and tiny audio/speech fixtures only
├── raw/.gitkeep
└── processed/.gitkeep

reports/
└── .gitkeep

scripts/
├── generate_dataset.py
├── synthesize_audio.py
├── run_benchmark.py
├── build_report.py
├── build_sft_dataset.py
├── train_lora.py
├── evaluate_lora.py
└── compare_quantization.py

tests/
├── unit/
├── integration/
└── e2e/
```

**Structure Decision**: Extend the existing Python monorepo layout with the exact advanced package, config, script, and notebook paths above. Keep shared schema, registry, model, pipeline, dataset, metrics, speech, fine-tuning, and report responsibilities in packages; keep user-facing commands in CLI/scripts; keep the Colab demo at `apps/notebook/colab_demo.ipynb`; keep heavyweight outputs outside tracked source.

## Complexity Tracking

No constitution violations are planned.

## Phase 0 Research Summary

See [research.md](research.md). Decisions cover adapter boundaries, Colab demo scope, LoRA/SFT data format, Russian dataset categories, multi-tool validation, speech-output artifact handling, quantized profile reporting, and CI boundaries.

## Phase 1 Design Summary

See [data-model.md](data-model.md), [quickstart.md](quickstart.md), and [contracts/](contracts/). Contracts define adapter capabilities, advanced CLI behavior, artifact extensions, and tool schemas for `units.convert`, `text.stress_ru`, and `calculator.simple`.

## Post-Design Constitution Check

- **Benchmark-first**: PASS. Quickstart defines smoke, Colab, LoRA comparison, speech, multi-tool, and quantized comparison evidence.
- **Tool validation**: PASS. Tool contracts require registry lookup and schema validation before execution for all supported tools.
- **JSON outputs**: PASS. Artifact contract preserves raw output, first-pass parse status, repair status, parsed envelope, validation errors, and structured failures.
- **Dataset discipline**: PASS. Data model defines dataset versions, deterministic splits, instruction-tuning records, and Russian category labels.
- **Modality parity**: PASS. Data model keeps text/audio semantic IDs and split alignment for Pipeline C/D where audio is evaluated.
- **Tool scope**: PASS. Allowed tool set is explicit and weather remains excluded.
- **Experiment artifacts**: PASS. Artifacts cover per-example JSONL, metrics summaries, speech paths, training/evaluation manifests, and comparison reports.
- **Modular boundary**: PASS. Plan identifies affected packages and avoids cross-package shortcuts.
- **Required tests**: PASS. Quickstart lists schema, parser repair, registry, metrics, dataset, adapter, pipeline, speech, and quantization smoke coverage.
- **Public API documentation**: PASS. Plan identifies new public interfaces requiring docstrings or equivalent comments.
- **CI coverage**: PASS. Smoke path uses mocks and fixtures without GPU or large downloads.
- **Full benchmarks**: PASS. Heavyweight real-model, training, speech, and quantized runs are manual or suitable-runner workflows.
- **Git hygiene**: PASS. Large outputs are local or workflow artifacts and not committed.
- **PR evidence**: PASS. Quickstart lists validation evidence expected for PR review.
