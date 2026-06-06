# CLI Contract: Bilingual Voice Benchmark Demo

## Commands

### Generate Dataset

```text
voxtool dataset generate --version <version> --output <examples.jsonl>
```

Required behavior:

- Writes 240 JSONL `BenchmarkExample` records.
- Enforces Russian/English balance, no-tool ratio, deterministic split, and expected output fields.
- Does not synthesize audio directly.

### Synthesize Audio

```text
voxtool audio synthesize --dataset <examples.jsonl> --output <audio_dir>
```

Required behavior:

- Produces one synthesized audio artifact per dataset example.
- Writes audio metadata JSONL with `audio_id`, `example_id`, transcript, synthesis settings, and file path.
- Does not require cloud services for MVP.

### Run Benchmark

```text
voxtool benchmark run --dataset <examples.jsonl> --audio-metadata <audio.jsonl> --pipelines A,B,C,D --adapter <mock|gemma3n|asr|textllm> --output <run_dir>
```

Required behavior:

- Saves raw output for every processed example.
- Saves parsed output when first-pass parsing or repair succeeds.
- Saves validation errors when parsing or schema validation fails.
- Optionally executes validated `units.convert` calls.
- Writes per-example pipeline outputs and aggregate metric summaries.

### Build Report

```text
voxtool report build --runs <run_dir> --output <report.md>
```

Required behavior:

- Reads pipeline artifacts and metric summaries.
- Writes final markdown report with required dataset, metric, WER, modality-gap, best-pipeline, and failure-analysis sections.

## Exit Codes

- `0`: command completed and wrote expected artifacts
- `1`: invalid command arguments or missing inputs
- `2`: schema validation failure in input dataset or config
- `3`: benchmark completed with model-output failures but artifacts were written
