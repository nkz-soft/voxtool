# Research: Bilingual Voice Benchmark Demo

## Dataset Format

**Decision**: Use JSONL as the canonical dataset and per-example run-output format.

**Rationale**: JSONL handles one record per semantic example, preserves nested expected tool calls, streams cleanly for CLI processing, and works well for both generated datasets and pipeline artifacts.

**Alternatives considered**: CSV was rejected for canonical datasets because nested tool calls and audio metadata become brittle. Parquet was rejected for canonical examples because it is less convenient for diffing small fixtures and hand inspection.

## Metrics Summary Format

**Decision**: Use CSV or Parquet for aggregate metrics summaries, with JSONL retained for per-example outputs.

**Rationale**: pandas can aggregate JSONL runs into tabular summaries, and CSV/Parquet are natural for report tables and downstream analysis.

**Alternatives considered**: Markdown-only metrics were rejected because they lose machine-readability. JSON-only aggregate metrics were rejected because tabular comparisons are central to the final report.

## Schema Modeling And Validation

**Decision**: Use Pydantic models for Python object validation and jsonschema for strict JSON Schema validation of model-output envelopes and `units.convert` tool calls.

**Rationale**: Pydantic gives typed internal models and clear errors, while jsonschema provides an explicit contract that can be stored, tested, and shared outside Python internals.

**Alternatives considered**: Pydantic-only validation was rejected because the spec requires JSON Schema validation. Hand-written validation was rejected because it is error-prone for nested envelope and tool-call rules.

## JSON Repair Behavior

**Decision**: Attempt exactly one retry or repair for invalid first-pass JSON, record repair success separately, and keep Parsable Tool Invocation Rate tied to first-pass valid JSON.

**Rationale**: This preserves model reliability as a primary metric while allowing downstream validation and execution to continue when repair succeeds.

**Alternatives considered**: Counting repaired JSON as parsable was rejected because it hides first-pass failures. Making invalid JSON terminal was rejected because failure analysis benefits from comparing repaired downstream behavior.

## ASR WER Evaluation

**Decision**: Use jiwer for WER and place transcript normalization in `packages/asr_eval`.

**Rationale**: jiwer is focused, widely used for WER, and supports deterministic transformation pipelines. A dedicated package keeps Russian/English normalization and WER independent from model adapters.

**Alternatives considered**: Custom WER logic was rejected because alignment details are easy to get wrong. Embedding WER in pipeline code was rejected because transcript evaluation should be reusable by Pipelines B-D.

## Plotting Scope

**Decision**: Use matplotlib only for plots in final reports.

**Rationale**: matplotlib is sufficient for simple bar charts and confusion-matrix visualizations without adding a heavier visualization stack.

**Alternatives considered**: seaborn/plotly were rejected for MVP to avoid unnecessary dependencies and UI complexity.

## Model Adapter Boundary

**Decision**: Define adapters for `Gemma3nAdapter`, `ASRAdapter`, `TextLLMAdapter`, and `MockModelAdapter` under `packages/model_runner`.

**Rationale**: A common adapter boundary lets pipelines A-D share orchestration and artifact handling while allowing deterministic tests and manual real-model experiments.

**Alternatives considered**: Pipeline-specific model code was rejected because it duplicates parsing and artifact logic. A single generic adapter was rejected because audio-capable, ASR-only, text-only, and mock behavior have different capabilities.

## TTS Generation

**Decision**: Put audio synthesis in `packages/tts_synth`, generate one audio file per text example, and write metadata linking audio files to dataset examples, synthesis settings, and reference transcripts.

**Rationale**: The benchmark needs reproducible audio/text pairing for modality-gap analysis. Metadata resolves the checklist gap around TTS reproducibility without requiring a cloud service.

**Alternatives considered**: Committing all generated audio was rejected for Git hygiene. Requiring a cloud TTS provider was rejected because the MVP must not require cloud services.

## MVP Exclusions

**Decision**: Exclude weather, cloud-service requirements, paid API requirements, GPU requirements for normal validation, and complex UI work.

**Rationale**: The benchmark’s value is in reproducible tool-use evaluation for `units.convert`, not broad assistant coverage or production UI.

**Alternatives considered**: Including weather was rejected by spec. A complex web UI was rejected because the requested demo can be served by CLI, notebook, and optional FastAPI endpoint.
