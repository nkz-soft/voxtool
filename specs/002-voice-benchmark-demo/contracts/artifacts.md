# Artifact Contract

## Dataset JSONL

Each line is a `BenchmarkExample`:

```json
{
  "example_id": "v1-en-length-0001",
  "dataset_version": "v1",
  "language": "en",
  "split": "test",
  "unit_family": "length",
  "text": "Convert 2 kilometers to meters.",
  "needs_tool": true,
  "expected_tool_call": {
    "tool": "units.convert",
    "arguments": {
      "value": 2,
      "from_unit": "kilometer",
      "to_unit": "meter"
    }
  },
  "expected_final_answer": "2 kilometers is 2000 meters.",
  "audio_id": "v1-en-length-0001-audio"
}
```

## Audio Metadata JSONL

Each line is an `AudioExample`:

```json
{
  "audio_id": "v1-en-length-0001-audio",
  "example_id": "v1-en-length-0001",
  "dataset_version": "v1",
  "language": "en",
  "split": "test",
  "reference_transcript": "Convert 2 kilometers to meters.",
  "audio_path": "data/generated/v1/audio/v1-en-length-0001.wav",
  "tts_engine": "local",
  "voice": "default-en",
  "sample_rate_hz": 16000,
  "duration_ms": 1800,
  "synthesis_settings": {}
}
```

## Pipeline Output JSONL

Each line is a `PipelineRun` record:

```json
{
  "run_id": "smoke-001",
  "pipeline": "A",
  "example_id": "v1-en-length-0001",
  "dataset_version": "v1",
  "model_adapter": "MockModelAdapter",
  "input_modality": "text",
  "raw_output": "{\"needs_tool\":true,...}",
  "parsed_output": {},
  "first_pass_parsable": true,
  "repair_attempted": false,
  "repair_success": false,
  "validation_error": null,
  "transcript": null,
  "tool_execution_result": {},
  "final_answer": "2 kilometers is 2000 meters."
}
```

## Metrics Summary

CSV or Parquet rows include:

- `run_id`
- `pipeline`
- `split`
- `language`
- `parsable_tool_invocation_rate`
- `repair_success_rate`
- `tool_decision_accuracy`
- `tool_call_exact_match`
- `argument_value_match`
- `argument_from_unit_match`
- `argument_to_unit_match`
- `precision`
- `recall`
- `false_alarm_rate`
- `wer`
- `modality_gap`

## Final Report

Markdown report includes:

- dataset summary
- per-pipeline metrics
- language-specific splits
- tool/no-tool confusion matrix
- ASR WER
- modality gap
- best-pipeline rationale
- categorized failure cases
