# Validation Evidence: Bilingual Voice Benchmark Demo (Phase 11)

Recorded on 2026-06-12 on Windows 11 with Python 3.11.15 and `uv`, following
`specs/002-voice-benchmark-demo/quickstart.md`. Covers tasks T096-T102.

## Lint

```text
> uv run ruff check .
All checks passed!

> uv run ruff format --check .
101 files already formatted
```

## Typecheck

```text
> uv run mypy
Success: no issues found in 100 source files
```

## Tests

```text
> uv run pytest    (PYTHONPATH=.)
116 passed, 1 warning in 6.49s
Coverage: 83% total (branch coverage enabled), coverage.xml written
```

## Dataset Generation

```text
> uv run python scripts/generate_dataset.py --version v1 --output data/generated/v1/examples.jsonl
wrote 240 dataset examples to data\generated\v1\examples.jsonl
```

240 examples: 120 Russian and 120 English, 15% no-tool, deterministic
70/15/15 split (verified by report dataset summary below).

## Audio Synthesis

```text
> uv run python scripts/synthesize_audio.py --dataset data/generated/v1/examples.jsonl --output data/generated/v1/audio
wrote 240 audio examples to data\generated\v1\audio\audio.jsonl
```

## Deterministic Smoke Benchmark (Mock Adapter, Pipelines A-D)

```text
> uv run python scripts/run_benchmark.py --pipeline A --dataset data/generated/v1/examples.jsonl --run-id smoke --model mock --output runs/smoke/pipeline-a.jsonl
> uv run python scripts/run_benchmark.py --pipeline B --audio-metadata data/generated/v1/audio/audio.jsonl --run-id smoke --model mock --output runs/smoke/pipeline-b.jsonl
> uv run python scripts/run_benchmark.py --pipeline C --audio-metadata data/generated/v1/audio/audio.jsonl --run-id smoke --model mock --output runs/smoke/pipeline-c.jsonl
> uv run python scripts/run_benchmark.py --pipeline D --audio-metadata data/generated/v1/audio/audio.jsonl --run-id smoke --model mock --output runs/smoke/pipeline-d.jsonl
```

Artifacts written (one `PipelineRun` JSONL per pipeline, 240 records each):

```text
runs/smoke/pipeline-a.jsonl
runs/smoke/pipeline-b.jsonl
runs/smoke/pipeline-c.jsonl
runs/smoke/pipeline-d.jsonl
```

## Report

```text
> uv run python scripts/build_report.py --dataset data/generated/v1/examples.jsonl --run runs/smoke/pipeline-a.jsonl --run runs/smoke/pipeline-b.jsonl --run runs/smoke/pipeline-c.jsonl --run runs/smoke/pipeline-d.jsonl --output reports/smoke-report.md --summary reports/smoke-summary.csv --plots-dir reports/plots
```

Outputs: `reports/smoke-report.md`, `reports/smoke-summary.csv`,
`reports/plots/confusion_matrix.png`, `reports/plots/exact_match.png`.

Report dataset summary confirms dataset discipline:

```text
- Total examples: 240
- Tool examples: 204
- No-tool examples: 36
- Language `en`: 120
- Language `ru`: 120
- Split `test`: 34
- Split `train`: 170
- Split `validation`: 36
```

Per-pipeline metrics include parsable rate, tool decision accuracy, exact
match, argument matches, precision/recall, WER for B/D, and modality gap for
audio pipelines against the Pipeline A baseline.

## CI Smoke Target

```text
> make benchmark-smoke
```

Runs audio synthesis on the fixture dataset, pipelines A-D with the mock
adapter (limit 30), and the report builder. Outputs under `reports/smoke/`:
`pipeline-{a,b,c,d}.jsonl`, `report.md`, `metrics-summary.csv`, `audio/`.
`ci.yml` runs this target on every push/PR; `benchmark-smoke.yml` uploads
`reports/smoke` plus a `benchmark-smoke-metrics` artifact with the metrics
summary and report.

## Demo Notebook

```text
> uv run --with nbclient --with ipykernel jupyter execute apps/notebook/voice_benchmark_demo.ipynb
[NbClientApp] Executing apps/notebook/voice_benchmark_demo.ipynb
```

Executed end to end without errors. Artifacts written under `runs/notebook/`:
`pipeline-{a,b,c,d}.jsonl` (240 records each), `audio/` (240 fixtures plus
`audio.jsonl`), `metrics-summary.csv`, and `report.md`. The notebook shows
Russian and English text examples, audio metadata, parsed JSON envelopes,
optional `units.convert` execution results, final answers, transcripts with
WER, the metrics summary, and the report.

## Git Hygiene

`git status` after the full validation run shows only source, docs, and
workflow changes; `data/generated/`, `runs/`, and report outputs remain
untracked per the artifact policy.

## Task IDs

T096, T097, T098, T099, T100, T101, T102 (issue #32, branch
`012-final-notebook-and-documentation`).
