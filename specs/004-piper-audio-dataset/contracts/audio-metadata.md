# Contract: Audio Metadata

## File

`audio.jsonl`

## Record Compatibility

Each line is one JSON object compatible with `AudioExample`.

Required fields:

- `audio_id`
- `example_id`
- `dataset_version`
- `language`
- `split`
- `reference_transcript`
- `audio_path`
- `tts_engine`
- `voice`
- `sample_rate_hz`
- `duration_ms`
- `synthesis_settings`

## Piper Record Expectations

- `tts_engine` is `piper`.
- `voice` identifies the selected Piper voice.
- `audio_path` points to a generated WAV file.
- `reference_transcript` exactly matches the source text used for synthesis.
- `dataset_version`, `language`, and `split` match the source text example.
- `synthesis_settings` includes enough information to identify the engine,
  selected voice, and local voice resources or configured voice mapping.

## Invalid Records

- Records missing source linkage fields are invalid.
- Records that claim Piper mode but point to silent fixture output are invalid.
- Partial manifests must not be treated as complete benchmark datasets.
