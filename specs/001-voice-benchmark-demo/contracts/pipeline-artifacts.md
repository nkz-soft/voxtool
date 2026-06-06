# Pipeline Artifact Contract

Every benchmark run writes a run directory outside Git-tracked generated
artifact exclusions.

## Required Files

```text
run/
├── inputs.jsonl
├── raw_outputs.jsonl
├── parsed_outputs.jsonl
├── validation_errors.jsonl
├── metrics.json
└── manifest.json
```

## `manifest.json`

Required fields:
- `run_id`
- `dataset_version`
- `split`
- `pipelines`
- `model_adapter`
- `created_at`
- `config_path`

## `inputs.jsonl`

One record per pipeline/example input.

Required fields:
- `run_id`
- `pipeline`
- `benchmark_example_id`
- `semantic_group_id`
- `language`
- `input_ref`

## `raw_outputs.jsonl`

One record per model or ASR output.

Required fields:
- `run_id`
- `pipeline`
- `benchmark_example_id`
- `stage`
- `raw_output`

## `parsed_outputs.jsonl`

One record per parse attempt.

Required fields:
- `run_id`
- `pipeline`
- `benchmark_example_id`
- `json_valid`
- `repair_attempted`
- `repair_successful`
- `parsed_output`

## `validation_errors.jsonl`

One record per validation failure.

Required fields:
- `run_id`
- `pipeline`
- `benchmark_example_id`
- `error_type`
- `message`
- `details`

## `metrics.json`

Required groups:
- `tool_use`
- `asr`
- `modality_gap`
- `artifact_summary`
