# Data Model: Bilingual Voice Benchmark Demo

## Unit

Canonical enum values:

- `meter`
- `kilometer`
- `centimeter`
- `millimeter`
- `gram`
- `kilogram`
- `pound`
- `ounce`
- `celsius`
- `fahrenheit`

Validation rules:

- Unit strings in model outputs must match the canonical enum.
- Length, mass, and temperature conversions are valid only within their compatible unit families.
- Temperature conversions use deterministic formulas.

## ToolCall

Fields:

- `tool`: required string, resolved against `ToolRegistry`
- `arguments`: required raw object validated against the resolved provider schema before execution

MVP `units.convert` arguments:

- `arguments.value`: required number
- `arguments.from_unit`: required Unit
- `arguments.to_unit`: required Unit

Relationships:

- Expected by `BenchmarkExample` when `needs_tool=true`.
- Emitted by `ModelOutputEnvelope.tool_call` when the model predicts tool use.
- Consumed by `ToolExecutor` only after registry lookup and provider argument validation succeed.
- Backward-compatible serialized field names may still use `tool_call`, but the internal common interface model is `ToolCall`.

## ToolProvider

Fields:

- `name`: required unique string, such as `units.convert`
- `description`: required human-readable string
- `argument_schema_name`: required identifier for the provider argument model
- `argument_schema`: required Pydantic model type used for validation
- `json_schema`: required JSON Schema export for prompts and validation
- `execute`: required deterministic method accepting validated arguments and returning `ToolResult`
- `deterministic`: required boolean, true for benchmark-executable providers

Validation rules:

- Provider names must be unique within a benchmark run.
- Provider names must be stable and non-empty.
- The JSON Schema export must correspond to the provider's Pydantic argument schema.
- Providers with duplicate names are rejected before pipeline execution begins.

## ToolRegistry

Fields:

- `providers`: mapping of tool name to `ToolProvider`
- `schema_export`: combined prompt/validation schema for all registered providers
- `manifest_export`: list of `ToolManifest` records built from registered providers

Validation rules:

- Unknown tool names resolve to structured failures.
- Registry schema exports are the source of truth for prompt construction and validation.
- Tool manifests are built only from registered providers.
- Pipelines must not import or call concrete providers directly.

## ToolManifest

Fields:

- `name`: registered provider name
- `description`: provider description
- `arguments_json_schema`: JSON Schema exported from the provider argument schema

Validation rules:

- Manifests are built only from `ToolRegistry`.
- Prompt construction consumes manifests, not concrete tool modules.
- Manifest names must match registered provider names.

## ModelOutputEnvelope

Fields:

- `needs_tool`: required boolean
- `tool_call`: required, either null or `ToolCall`
- `final_answer`: required string
- `transcript`: optional string for transcript-capable pipelines

Validation rules:

- If `needs_tool=false`, `tool_call` must be null.
- If `needs_tool=true`, `tool_call` must name a registered tool and include arguments valid for that tool.
- Pipeline C outputs include `transcript`.
- Pipeline B transcript output may be recorded without a tool-call envelope because it is transcript-only.

## BenchmarkExample

Fields:

- `example_id`: stable unique string
- `dataset_version`: string
- `language`: `ru` or `en`
- `split`: `train`, `validation`, or `test`
- `unit_family`: `length`, `mass`, `temperature`, or `none`
- `text`: reference request text
- `needs_tool`: expected boolean
- `expected_tool_call`: null or `ToolCall`
- `expected_final_answer`: string
- `audio_id`: stable ID of linked synthesized audio

Validation rules:

- Dataset contains exactly 240 records: 120 Russian and 120 English.
- 15% of records overall and per language have `needs_tool=false`.
- Splits use deterministic 70/15/15 allocation stratified by language, tool/no-tool label, and unit family.
- Every record has one linked `AudioExample`.

## AudioExample

Fields:

- `audio_id`: stable unique string
- `example_id`: related `BenchmarkExample`
- `dataset_version`: string
- `language`: `ru` or `en`
- `split`: inherited from benchmark example
- `reference_transcript`: expected transcript text
- `audio_path`: local artifact path
- `tts_engine`: synthesis adapter name
- `voice`: optional voice identifier
- `sample_rate_hz`: integer
- `duration_ms`: optional integer
- `synthesis_settings`: object with deterministic generation settings

Validation rules:

- Audio examples must retain the same semantic ID and split as their text counterpart.
- Audio metadata is stored in JSONL so generated files can remain outside Git.

## PipelineRun

Fields:

- `run_id`: unique string
- `pipeline`: `A`, `B`, `C`, or `D`
- `example_id`: related benchmark example
- `dataset_version`: string
- `model_adapter`: adapter name
- `input_modality`: `text` or `audio`
- `raw_output_path`: path to raw output artifact
- `parsed_output`: null or `ModelOutputEnvelope`
- `first_pass_parsable`: boolean
- `repair_attempted`: boolean
- `repair_success`: boolean
- `validation_error`: null or structured error
- `structured_failures`: list of structured parsing, validation, registry, or execution failures
- `transcript`: optional string
- `tool_execution_result`: optional `ToolResult`
- `final_answer`: optional string

State transitions:

1. Pending input
2. Raw output captured
3. Parsed or repair attempted
4. Schema validated, registry-resolved, or validation/registry failure recorded
5. Optionally executed through `ToolExecutor` if validation passed and execution enabled
6. Metrics recorded

## ToolResult

Fields:

- `tool`: resolved provider name
- `arguments`: validated `ToolCall.arguments`
- `result`: provider-specific deterministic result object
- `result_value`: optional number for `units.convert`
- `result_unit`: optional Unit for `units.convert`
- `rounded_display`: optional string for `units.convert`
- `execution_error`: null or string

Validation rules:

- Created only by `ToolExecutor` after registry lookup and provider argument validation succeed.
- Execution errors are represented as structured failures and do not stop unrelated examples.
- `units.convert` results use deterministic rounding rules documented by implementation.
- Backward-compatible serialized field names may still use `tool_execution_result`, but the internal common interface model is `ToolResult`.

## StructuredToolFailure

Fields:

- `failure_type`: `unknown_tool`, `duplicate_tool_provider`, `invalid_arguments`, or `execution_error`
- `tool`: requested or provider tool name when available
- `message`: human-readable diagnostic
- `details`: machine-readable diagnostic object
- `stage`: `registry`, `validation`, or `execution`

Validation rules:

- Unknown tools and invalid arguments are never executed.
- Execution errors retain the original validated tool name and arguments summary.

## MetricResult

Fields:

- `run_id`: related benchmark run batch
- `pipeline`: `A`, `B`, `C`, or `D`
- `split`: evaluated split or `all`
- `language`: `ru`, `en`, or `all`
- `parsable_tool_invocation_rate`: number
- `repair_success_rate`: number
- `tool_decision_accuracy`: number
- `tool_call_exact_match`: number
- `argument_value_match`: number
- `argument_from_unit_match`: number
- `argument_to_unit_match`: number
- `precision`: number
- `recall`: number
- `false_alarm_rate`: number
- `wer`: optional number
- `modality_gap`: optional number

Validation rules:

- Parsability rate counts only first-pass valid JSON envelopes.
- Tool-call exact match for the MVP dataset requires correct `needs_tool`, tool name, value, source unit, and target unit.
- Partially correct tool calls are not exact matches but contribute to per-field argument diagnostics.

## FailureCase

Fields:

- `run_id`
- `pipeline`
- `example_id`
- `language`
- `failure_category`: JSON parsing, repair failed, schema validation, unknown tool, duplicate tool provider, invalid arguments, tool decision, tool name, numeric value, source unit, target unit, transcript, execution, answer
- `expected_summary`
- `observed_summary`
- `raw_output_path`

Relationships:

- Included in the final report and linked to per-example pipeline outputs.
