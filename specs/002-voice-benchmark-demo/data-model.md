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

## ToolInvocation

Fields:

- `tool`: required string, exactly `units.convert`
- `arguments.value`: required number
- `arguments.from_unit`: required Unit
- `arguments.to_unit`: required Unit

Relationships:

- Expected by `BenchmarkExample` when `needs_tool=true`.
- Emitted by `ModelOutputEnvelope.tool_call` when the model predicts tool use.
- Consumed by `ToolExecutionResult` only after schema validation succeeds.

## ModelOutputEnvelope

Fields:

- `needs_tool`: required boolean
- `tool_call`: required, either null or `ToolInvocation`
- `final_answer`: required string
- `transcript`: optional string for transcript-capable pipelines

Validation rules:

- If `needs_tool=false`, `tool_call` must be null.
- If `needs_tool=true`, `tool_call` must be a valid `units.convert` invocation.
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
- `expected_tool_call`: null or `ToolInvocation`
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
- `transcript`: optional string
- `tool_execution_result`: optional `ToolExecutionResult`
- `final_answer`: optional string

State transitions:

1. Pending input
2. Raw output captured
3. Parsed or repair attempted
4. Schema validated or validation failed
5. Optionally executed if validation passed and execution enabled
6. Metrics recorded

## ToolExecutionResult

Fields:

- `tool`: `units.convert`
- `arguments`: `ToolInvocation.arguments`
- `result_value`: number
- `result_unit`: Unit
- `rounded_display`: string
- `execution_error`: null or string

Validation rules:

- Created only after schema validation succeeds.
- Conversion result uses deterministic rounding rules documented by implementation.

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
- Tool-call exact match requires correct `needs_tool`, tool name, value, source unit, and target unit.
- Partially correct tool calls are not exact matches but contribute to per-field argument diagnostics.

## FailureCase

Fields:

- `run_id`
- `pipeline`
- `example_id`
- `language`
- `failure_category`: JSON parsing, repair failed, schema validation, tool decision, tool name, numeric value, source unit, target unit, transcript, execution, answer
- `expected_summary`
- `observed_summary`
- `raw_output_path`

Relationships:

- Included in the final report and linked to per-example pipeline outputs.
