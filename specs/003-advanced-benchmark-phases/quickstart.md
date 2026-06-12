# Quickstart: Advanced Benchmark Phases

## Prerequisites

- Python 3.11+
- `uv` for dependency management
- Existing smoke validation does not require GPU, large model downloads, remote services, training, or speech generation
- Google Colab or equivalent runtime is used for real-model demos and optional heavyweight workflows

## Install

```powershell
uv sync --all-groups
```

For notebook or real-model experiments, install the optional extras documented by the adapter or notebook configuration. Ordinary CI must keep using the lightweight mock path.

## Run Ordinary CI-Style Validation

```powershell
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv run python scripts/run_benchmark.py --pipeline A --dataset data/fixtures/sample.jsonl --run-id advanced-smoke --model mock --output runs/advanced-smoke/pipeline-a.jsonl --limit 10
```

Expected result:

- no large model downloads
- no GPU requirement
- adapter contract tests pass with mocks
- tool registry tests cover `units.convert`, `text.stress_ru`, and `calculator.simple`
- smoke benchmark writes raw output, parsed output, validation errors, execution results, final answers, and metrics

## Open The Colab Demo

Open `apps/notebook/colab_demo.ipynb`.

Expected notebook flow:

- install optional notebook dependencies
- clone or load the repository
- load a small fixture or generated sample dataset
- select `voxtral`, `qwen`, `gemma`, or `mock` from `configs/models/*.yaml`
- run Pipeline A on text examples
- optionally upload an audio file and run Pipeline C or D when adapter and runtime capabilities allow audio
- run inference, validate the JSON tool call, execute the tool, show the final answer, and display metrics

## Prepare Russian Instruction-Tuning Data

```powershell
uv run python scripts/build_sft_dataset.py --config configs/datasets/ru_toolbench.yaml --version advanced-ru-v1 --output data/generated/advanced-ru-v1/instruction.jsonl
```

Expected result:

- JSONL instruction-tuning records
- each record contains `instruction`, `input`, `expected_output_json`, `locale`, `tool_name`, `split`, `source`, and `difficulty`
- `expected_output_json` uses the same ModelOutput JSON contract as the benchmark
- deterministic train, validation, and test split labels
- Russian categories for `units_convert`, `no_tool`, `ambiguous_wording`, and `speech_style`
- optional multi-tool records when registry support is enabled

## Run LoRA/SFT Workflow

Manual or suitable-runner workflow:

```powershell
uv run python scripts/train_lora.py --config configs/finetuning/lora_qwen.yaml --dataset data/generated/advanced-ru-v1/instruction.jsonl --output runs/lora/ru
uv run python scripts/evaluate_lora.py --dataset data/generated/advanced-ru-v1/instruction.jsonl --base-model qwen --lora-model runs/lora/ru --split test --output runs/lora/ru-eval
```

Expected report contents:

- `parsable_rate`
- `tool_decision_accuracy`
- `tool_call_exact_match`
- `argument_exact_match`
- `false_alarm_rate`
- Russian-only metrics
- English subset metrics when English examples are included
- no-tool subset metrics
- per-tool subset metrics
- before/after deltas against the base model

Generated checkpoints and full outputs stay outside Git.

## Run Multi-Tool Evaluation

```powershell
uv run python scripts/run_benchmark.py --pipeline A --dataset data/fixtures/multitool_sample.jsonl --run-id multitool-smoke --model mock --tools units.convert,text.stress_ru,calculator.simple --output runs/multitool-smoke/pipeline-a.jsonl
uv run python scripts/build_report.py --runs runs/multitool-smoke --output reports/multitool-smoke.md --summary reports/multitool-smoke.csv
```

Expected result:

- unsupported tools are rejected as structured failures
- each supported tool routes through `ToolRegistry` and `ToolExecutor`
- per-tool metrics appear for all tools present in the subset

## Run Speech Output Demo

```powershell
uv run python scripts/run_benchmark.py --pipeline A --dataset data/fixtures/sample.jsonl --run-id speech-demo --model mock --speech-output mock --output runs/speech-demo/pipeline-a.jsonl --limit 3
```

Expected result:

- final answers are produced before speech generation
- speech output paths are recorded for generated examples
- disabled, skipped, or failed speech generation is represented explicitly

## Compare Quantized Inference

Manual or suitable-runner workflow:

```powershell
uv run python scripts/compare_quantization.py --dataset data/fixtures/sample.jsonl --model qwen --base-profile configs/inference/full_precision.yaml --quantized-profile configs/inference/quantized_4bit.yaml --limit 10 --output runs/quantization/qwen-4bit
```

Expected result:

- paired base and quantized outputs for the same examples
- quality metrics for both profiles
- memory and usability trade-off notes in the comparison summary
- latency per example when measured
- `parsable_rate`, `tool_call_exact_match`, and quality delta against the non-quantized baseline

## Build Advanced Report

```powershell
uv run python scripts/build_report.py --runs runs/advanced-smoke --output reports/advanced-smoke.md --summary reports/advanced-smoke.csv
```

Expected report contents:

- adapter and inference profile summary
- Russian-only metrics where Russian examples are present
- per-tool metrics
- optional speech-output status
- base-versus-adapted and base-versus-quantized comparisons when supplied
- categorized failure cases

## Required Test Coverage

- `ModelAdapter` capability selection and unsupported-runtime handling
- `ModelAdapter.generate_text(prompt, config) -> ModelResponse`
- Voxtral, Qwen, and Gemma adapter contract behavior through mocks or smoke fixtures
- Voxtral, Qwen, and Gemma import/config tests only for ordinary CI
- canonical JSON parsing and one repair attempt
- strict tool schema validation and registry routing
- `text.stress_ru` and `calculator.simple` provider schemas and deterministic execution
- Russian dataset category generation/import and deterministic splits
- LoRA evaluation metric comparison
- speech-output artifact status handling
- quantized profile selection and paired comparison metrics
- pipeline orchestration for A, C, and D with mock adapters

## PR Evidence

Include:

- linked Spec Kit task IDs
- ruff output
- format-check output
- mypy output
- pytest output
- deterministic smoke benchmark command and artifact path
- generated report path or summary
- manual Colab, LoRA, speech, real-model, or quantization artifact paths when those workflows are changed
