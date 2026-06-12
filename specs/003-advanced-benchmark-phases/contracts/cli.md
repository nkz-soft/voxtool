# CLI Contract: Advanced Benchmark Phases

## Prepare Instruction Data

```text
voxtool dataset build-sft --config <dataset.yaml> --version <version> --output <instruction.jsonl>
```

Required behavior:

- Writes instruction-tuning JSONL records.
- Each record contains `instruction`, `input`, `expected_output_json`, `locale`, `tool_name`, `split`, `source`, and `difficulty`.
- Produces deterministic train, validation, and test split labels.
- Includes required Russian categories for Russian workflows.
- Validates expected JSON envelopes before writing records.

## Run Benchmark With Adapter

```text
voxtool benchmark run --dataset <examples.jsonl> --pipelines A,C,D --adapter <mock|voxtral|qwen|gemma> --inference-profile <profile> --tools <tool-list> --output <run_dir>
```

Required behavior:

- Selects adapters by declared capabilities.
- Saves raw model output before parsing.
- Performs canonical parsing, repair, validation, registry lookup, optional execution, and metrics.
- Records unsupported adapter/runtime combinations explicitly.
- Does not require real-model downloads in ordinary CI.

## Train LoRA

```text
voxtool train lora --config <configs/finetuning/lora_gemma.yaml|configs/finetuning/lora_qwen.yaml> --dataset <instruction.jsonl> --output <run_dir>
```

Required behavior:

- Reads instruction-tuning JSONL.
- Records config, dataset version, split usage, and output artifact paths.
- Writes checkpoints and full training outputs outside Git-tracked paths.

## Evaluate Adapters

```text
voxtool eval lora --dataset <instruction.jsonl> --base-model <adapter> --lora-model <adapter-or-checkpoint> --split test --output <run_dir>
```

Required behavior:

- Evaluates base and candidate on the same examples.
- Writes per-example outputs and aggregate metrics.
- Reports base model, LoRA model, Russian subset, English subset, no-tool subset, per-tool subset, and before/after deltas.

## Generate Speech Output

```text
voxtool speech synthesize --input-runs <pipeline.jsonl> --provider <mock|local> --output <audio_dir>
```

Required behavior:

- Reads final answers.
- Generates or mocks speech audio when enabled.
- Records speech output paths and generation status.
- Stays disabled in ordinary CI except mock or fixture checks.

## Compare Quantization

```text
voxtool eval quantization --dataset <examples.jsonl> --adapter <adapter> --base-profile configs/inference/full_precision.yaml --quantized-profile <configs/inference/quantized_8bit.yaml|configs/inference/quantized_4bit.yaml> --output <run_dir>
```

Required behavior:

- Runs paired base and quantized evaluations on the same examples.
- Reports quality metrics and resource trade-off notes.
- Reports memory notes if available, latency per example if measured, `parsable_rate`, `tool_call_exact_match`, and quality delta against the non-quantized baseline.
- Fails configuration validation when a selected profile is unsupported.

## Exit Codes

- `0`: command completed and wrote expected artifacts
- `1`: invalid command arguments or missing inputs
- `2`: schema validation failure in input dataset, tool config, adapter config, or training config
- `3`: benchmark completed with model-output failures but artifacts were written
- `4`: requested adapter, runtime capability, speech provider, or quantized profile is unsupported
