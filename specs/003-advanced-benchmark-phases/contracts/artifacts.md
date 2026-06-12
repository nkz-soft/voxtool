# Advanced Artifact Contract

## Instruction-Tuning JSONL

Each line is an `InstructionTuningRecord`:

```json
{
  "record_id": "advanced-ru-v1-0001",
  "dataset_version": "advanced-ru-v1",
  "instruction": "Верни JSON для вызова инструмента, если инструмент нужен.",
  "input": "Сконвертируй 2 километра в метры.",
  "expected_output_json": "{\"needs_tool\":true,\"tool_call\":{\"tool\":\"units.convert\",\"arguments\":{\"value\":2,\"from_unit\":\"kilometer\",\"to_unit\":\"meter\"}},\"final_answer\":\"2 километра это 2000 метров.\"}",
  "locale": "ru-RU",
  "tool_name": "units.convert",
  "split": "train",
  "source": "configs/datasets/ru_units_convert.yaml",
  "difficulty": "easy",
  "category": "units_convert",
  "expected_tool_call": {
    "tool": "units.convert",
    "arguments": {
      "value": 2,
      "from_unit": "kilometer",
      "to_unit": "meter"
    }
  },
  "expected_final_answer": "2 километра это 2000 метров.",
  "source_example_id": "advanced-ru-v1-units-0001"
}
```

Required behavior:

- `expected_output_json` must be parsable as the canonical model-output envelope.
- Split assignment is deterministic.
- Russian datasets must include required category labels.

## Advanced Pipeline Output Fields

Pipeline output JSONL keeps the existing `PipelineRun` shape and may add:

```json
{
  "adapter_id": "qwen",
  "adapter_capabilities": {
    "supports_text_input": true,
    "supports_audio_input": false,
    "supports_tool_call_output": true
  },
  "inference_profile": "base",
  "tool_manifest_snapshot": [
    {
      "name": "units.convert",
      "description": "Convert units.",
      "arguments_json_schema": {}
    }
  ],
  "speech_output": {
    "generation_status": "generated",
    "speech_output_path": "runs/speech-demo/audio/example.wav",
    "generation_error": null
  },
  "runtime_skip_reason": null
}
```

Required behavior:

- Existing raw output, parsing, repair, validation, execution, final answer, and metric fields remain intact.
- Speech output is optional and may be `disabled`, `skipped`, or `failed`.
- Runtime skips are distinct from model-output failures.

## Metrics Summary Extensions

CSV or Parquet rows may include:

- `tool`
- `category`
- `parsable_rate`
- `tool_decision_accuracy`
- `tool_call_exact_match`
- `argument_exact_match`
- `false_alarm_rate`
- `execution_success_rate`
- `latency_ms_per_example`
- `memory_note`
- `russian_only`
- `base_value`
- `candidate_value`
- `delta`

Required behavior:

- Per-tool metrics are reported for supported tools present in the evaluated subset.
- Russian-only metrics are reported for Russian adaptation workflows.
- Base-versus-LoRA and base-versus-quantized comparisons use paired examples.

## Speech Output Artifact

```json
{
  "speech_output_id": "speech-demo-0001",
  "run_id": "speech-demo",
  "example_id": "advanced-en-0001",
  "input_final_answer": "2 kilometers is 2000 meters.",
  "speech_output_path": "runs/speech-demo/audio/advanced-en-0001.wav",
  "speech_provider": "mock",
  "generation_status": "generated",
  "generation_error": null
}
```

Required behavior:

- Speech generation requires a final answer.
- Speech failures do not erase tool-call metrics.
- Generated audio files stay outside Git except tiny fixtures.
