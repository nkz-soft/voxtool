# CLI Contract

The CLI exposes deterministic commands for benchmark and demo workflows. Commands
return nonzero exit codes on validation or execution failures and write artifacts
to caller-provided output paths.

## Commands

### `voxtool dataset generate`

Generates a versioned RU/EN dataset with deterministic splits.

Required inputs:
- Experiment or dataset config path.
- Output directory.

Required outputs:
- Dataset metadata with version and split rule.
- Example records with stable IDs and semantic group IDs.

### `voxtool audio synth`

Synthesizes audio for dataset examples.

Required inputs:
- Dataset path.
- Output directory.

Required outputs:
- Audio manifest linked to benchmark example IDs.
- Generated audio files outside Git-tracked fixture paths.

### `voxtool benchmark run`

Runs pipelines A-D for selected examples.

Required inputs:
- Experiment config.
- Model adapter name.
- Limit or dataset selection.
- Output directory.

Required outputs:
- Inputs.
- Raw model outputs.
- Parsed outputs.
- Validation errors.
- Metrics.

### `voxtool report build`

Builds markdown report tables from benchmark outputs.

Required inputs:
- Benchmark output directory.
- Output report path.

Required outputs:
- Markdown report.
- Tables for tool-use, ASR, and modality-gap metrics.
