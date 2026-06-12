# Data Model: Advanced Benchmark Phases

## ModelAdapter

Fields:

- `adapter_id`: stable adapter identifier, such as `voxtral`, `qwen`, `gemma`, or `mock`
- `model_family`: supported family label
- `generate_text(prompt, config)`: common text-generation operation returning `ModelResponse`
- `supports_audio_input`: boolean capability flag
- `supports_text_input`: boolean capability flag
- `supports_lora`: boolean capability flag
- `supports_quantization`: boolean capability flag
- `capabilities`: `AdapterCapabilities`
- `inference_profile`: selected `InferenceProfile`
- `resource_requirements`: optional memory, accelerator, and runtime notes

Validation rules:

- Adapter IDs must be unique within a run.
- Pipelines may select an adapter only when declared capabilities satisfy the requested modality and output requirements.
- Unsupported capabilities produce structured skipped-capability or configuration failures before model execution.

## AdapterCapabilities

Fields:

- `supports_text_input`: boolean
- `supports_audio_input`: boolean
- `supports_lora`: boolean
- `supports_quantization`: boolean
- `supports_transcript_output`: boolean
- `supports_tool_call_output`: boolean
- `supported_pipelines`: list containing any of `A`, `C`, `D`

Validation rules:

- Pipeline A requires text input and tool-call output.
- Pipeline C requires audio input, transcript output, and tool-call output.
- Pipeline D requires a transcript source plus text input and tool-call output.

## ModelResponse

Fields:

- `raw_output`: exact model text returned before parsing
- `parsed_output`: optional canonical model-output envelope after parsing or repair
- `metadata`: optional adapter, profile, token, timing, or runtime details
- `error`: optional adapter-level error before parsing

Validation rules:

- `raw_output` is saved for every completed model call.
- Parsing and schema validation occur outside the adapter through the benchmark pipeline.
- Adapter errors are logged as model execution failures and do not bypass artifact writing.

## InferenceProfile

Fields:

- `profile_id`: stable profile name
- `precision_mode`: `full_precision`, `8bit`, `4bit`, `gguf_or_local_runtime`, or `mock`
- `model_family`: compatible model family or `all`
- `config_path`: optional config reference
- `memory_note`: expected memory behavior or measured summary
- `quality_note`: expected quality trade-off or measured summary

Validation rules:

- A quantized profile must declare model-family compatibility.
- Base-versus-quantized comparison must evaluate the same examples with comparable adapter settings.
- Profile configs are stored in `configs/inference/full_precision.yaml`, `configs/inference/quantized_8bit.yaml`, and `configs/inference/quantized_4bit.yaml`.

## ColabDemoRun

Fields:

- `run_id`: unique run identifier
- `dataset_version`: sample dataset or fixture version
- `adapter_id`: selected adapter
- `pipelines`: list of executed pipelines
- `examples_processed`: integer count
- `runtime_capabilities`: captured runtime notes
- `metrics_table_path`: optional saved metrics table

Relationships:

- Contains zero or more `PipelineRun` records.
- Uses `ModelAdapter` and `InferenceProfile`.

## InstructionTuningRecord

Fields:

- `record_id`: stable unique string
- `dataset_version`: version identifier
- `language`: `ru` or `en`
- `instruction`: instruction text
- `input`: user input or task input text
- `expected_output_json`: expected canonical model-output envelope as JSON text
- `locale`: locale label, such as `ru-RU` or `en-US`
- `tool_name`: expected tool name or `none`
- `split`: `train`, `validation`, or `test`
- `source`: source dataset or generation rule identifier
- `difficulty`: difficulty label
- `category`: `units_convert`, `no_tool`, `ambiguous_wording`, `speech_style`, `multi_tool`, or `other`
- `prompt`: instruction text presented to the model
- `expected_output`: canonical JSON envelope text
- `expected_tool_call`: optional `ToolCall`
- `expected_final_answer`: expected answer text or answer behavior label
- `source_example_id`: optional benchmark example relationship

Validation rules:

- Russian LoRA datasets must include `units_convert`, `no_tool`, `ambiguous_wording`, and `speech_style` categories.
- Splits are deterministic and preserve category, language, and tool/no-tool balance where practical.
- `expected_output_json` must be parsable as the canonical model-output envelope used by the benchmark.

## AdaptationRun

Fields:

- `run_id`: unique comparison identifier
- `base_adapter_id`: base model adapter
- `adapted_adapter_id`: adapted model adapter or checkpoint reference
- `dataset_version`: evaluated dataset version
- `evaluation_split`: split or subset label
- `training_config_path`: configuration reference
- `base_metrics_path`: metrics for base model
- `adapted_metrics_path`: metrics for adapted model
- `delta_metrics_path`: before/after comparison summary

Validation rules:

- Base and adapted evaluations must use the same examples.
- Russian-only metrics and deltas must be present for Russian adaptation reports.
- Checkpoints and full outputs are external artifacts and are not committed.

## ToolProvider Extensions

Core registry entities:

- `ToolDefinition`: stable tool name, description, args model, JSON schema, deterministic executor reference, examples, and metrics grouping label
- `ToolRegistry`: unique mapping of tool names to definitions
- `ToolExecutor`: execution boundary for validated tool calls
- `ToolSchemaValidator`: schema-validation boundary that rejects invalid calls before execution

Additional supported providers:

- `text.stress_ru`: places stress marks in Russian text or selected words.
- `calculator.simple`: performs deterministic simple arithmetic.

Validation rules:

- Provider names must be unique.
- Provider schemas must be exported through `ToolRegistry`.
- Pipelines must not execute a provider directly.
- Unknown tool calls are structured failures.
- Each tool must include a Pydantic args model, JSON schema, deterministic executor, tests, examples, and metrics grouping.

## SpeechSynthesizer

Fields:

- `synthesizer_id`: stable provider identifier
- `provider`: `piper`, `edge_tts`, or `mock`
- `voice`: optional voice identifier
- `sample_rate_hz`: optional sample rate
- `config_path`: optional config reference

Validation rules:

- Speech synthesizers accept final text answers and produce `SpeechOutputArtifact` records.
- Real speech synthesis is optional and disabled in ordinary CI.
- Mock or fixture synthesizers may be used in CI.

## SpeechOutputArtifact

Fields:

- `speech_output_id`: unique identifier
- `run_id`: related run
- `example_id`: related example
- `input_final_answer`: text answer used for speech generation
- `speech_output_path`: generated audio path, null on failure
- `speech_provider`: selected speech provider or mock
- `generation_status`: `generated`, `disabled`, `skipped`, or `failed`
- `generation_error`: optional structured error

Validation rules:

- Speech generation can occur only after a final answer exists.
- Speech failures do not erase tool-call evaluation results.
- Generated speech files are external artifacts except tiny fixtures.

## AdvancedMetricResult

Fields:

- `run_id`
- `pipeline`
- `split`
- `language`
- `tool`: supported tool name or `all`
- `category`: dataset category or `all`
- `parsable_rate`
- `repair_success_rate`
- `tool_decision_accuracy`
- `tool_call_exact_match`
- `argument_exact_match`
- `false_alarm_rate`
- `execution_success_rate`
- `russian_only`: boolean
- `base_value`: optional number for comparisons
- `candidate_value`: optional number for comparisons
- `delta`: optional number

Validation rules:

- Per-tool metrics must include at least `units.convert`, `text.stress_ru`, and `calculator.simple` when those tools appear in the evaluated subset.
- Fine-tuning reports must include Russian-only metrics.
- Quantized comparisons must use paired examples for base and quantized values.

## AdvancedPipelineRun Extension

Additional fields on `PipelineRun`:

- `adapter_id`
- `adapter_capabilities`
- `inference_profile`
- `tool_manifest_snapshot`
- `speech_output`: optional `SpeechOutputArtifact`
- `runtime_skip_reason`: optional string for unsupported adapter/runtime combinations

Validation rules:

- Existing parsing, repair, validation, registry, execution, and metric fields remain required for processed model-output examples.
- Runtime skips must be counted separately from model failures.
