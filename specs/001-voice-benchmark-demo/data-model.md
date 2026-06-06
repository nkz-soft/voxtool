# Data Model: Multilingual Voice Benchmark Demo

## BenchmarkExample

Represents one semantic request used by text and audio evaluations.

**Fields**:
- `id`: Stable unique identifier.
- `dataset_version`: Dataset version string.
- `split`: One of `train`, `validation`, `test`, or `smoke`.
- `language`: `en` or `ru`.
- `semantic_group_id`: Shared identifier linking equivalent text/audio variants.
- `input_text`: Canonical text request.
- `requires_tool`: Boolean tool-use label.
- `expected_tool_name`: `units.convert` when `requires_tool` is true.
- `expected_arguments`: Expected value, source unit, and target unit.
- `expected_answer`: Concise expected answer or answer pattern.
- `tags`: Scenario tags such as `tool-required`, `no-tool`, `invalid-json`,
  `invalid-schema`, `temperature`, `mass`, or `length`.

**Validation rules**:
- `id` is unique within a dataset version.
- `split` is deterministic from dataset metadata.
- `expected_tool_name` is absent when `requires_tool` is false.
- Tool-required examples use only supported `units.convert` units.

## AudioFixture

Represents a small committed fixture or generated audio artifact tied to a
benchmark example.

**Fields**:
- `id`: Stable unique identifier.
- `benchmark_example_id`: Linked `BenchmarkExample`.
- `semantic_group_id`: Same semantic group as the source example.
- `language`: `en` or `ru`.
- `audio_path`: Local path or artifact path.
- `transcript_reference`: Expected or source transcript text.
- `fixture_kind`: `small-fixture` or `generated-artifact`.

**Validation rules**:
- Small fixtures may be committed only when bounded and required for tests.
- Generated audio is excluded from Git.
- Audio and text examples share semantic IDs for modality-gap metrics.

## ToolInvocation

Represents a structured model-produced tool request.

**Fields**:
- `tool_name`: Must be `units.convert`.
- `arguments.value`: Numeric input value.
- `arguments.from_unit`: Source unit.
- `arguments.to_unit`: Target unit.

**Validation rules**:
- Tool invocation must validate before execution.
- Unsupported tool names fail validation.
- Missing, nonnumeric, or unsupported unit arguments fail validation.

## ModelOutput

Represents raw and parsed output from a model adapter.

**Fields**:
- `raw_output`: Original model output string.
- `parsed_output`: Parsed JSON object when available.
- `json_valid`: Boolean JSON parse result.
- `repair_attempted`: Boolean parser-repair marker.
- `repair_successful`: Boolean repair result.
- `validation_errors`: List of parse or schema validation errors.

**Validation rules**:
- Invalid first-pass JSON is a failure even if repair succeeds for analysis.
- Raw output is always saved.

## PipelineRun

Represents one execution of one pipeline for one benchmark example.

**Fields**:
- `run_id`: Unique run identifier.
- `pipeline`: `A`, `B`, `C`, or `D`.
- `benchmark_example_id`: Linked example.
- `input_ref`: Text, audio fixture, or generated artifact reference.
- `transcript`: Transcript when produced.
- `model_output`: Linked `ModelOutput`.
- `tool_invocation`: Linked `ToolInvocation` when present.
- `tool_executed`: Boolean execution marker.
- `tool_result`: Conversion result when executed.
- `answer`: Concise human-readable answer.
- `started_at` / `finished_at`: Run timestamps.

**Validation rules**:
- Pipeline A starts from text.
- Pipeline B produces transcript only.
- Pipeline C produces transcript and tool decision in one pass.
- Pipeline D produces ASR transcript before text-model tool decision.
- Inputs, raw outputs, parsed outputs, validation errors, and metrics are saved.

## MetricResult

Represents evaluated outcomes for a run or comparison group.

**Fields**:
- `run_id`: Linked `PipelineRun` when run-level.
- `semantic_group_id`: Linked group when comparing modalities.
- `metric_name`: Metric identifier.
- `metric_value`: Numeric, boolean, or string metric value.
- `passed`: Boolean pass/fail marker when applicable.
- `details`: Short diagnostic payload.

**Metric groups**:
- Tool-use: JSON validity, schema validity, tool selection, argument accuracy,
  execution correctness, answer correctness.
- ASR: transcript exact/normalized match and word error rate.
- Modality gap: paired text/audio difference by semantic group and pipeline.

## WorkflowArtifact

Represents an automation output retained outside Git.

**Fields**:
- `workflow_name`: `ci`, `benchmark-smoke`, `report`, or `release`.
- `artifact_name`: Uploaded artifact name.
- `retention_days`: `14` for PR coverage/smoke, `90` for manual report/release.
- `contents`: Coverage, smoke metrics, full report, or release report artifact.

## GitHubWorkItem

Represents GitHub issue and PR process records.

**Fields**:
- `type`: `Feature Task`, `Benchmark Experiment`, `Bug`, or
  `Documentation/Process`.
- `speckit_task_ids`: Required for pull requests.
- `validation_evidence`: CI, smoke benchmark, manual report, or release links.
- `hypothesis`: Required for Benchmark Experiment.
- `pipeline`: Required for Benchmark Experiment.
- `setup`: Required for Benchmark Experiment.
- `metrics`: Required for Benchmark Experiment.
- `result`: Required for Benchmark Experiment.
