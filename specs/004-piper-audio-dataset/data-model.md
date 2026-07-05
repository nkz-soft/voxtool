# Data Model: Piper Audio Dataset

## Text Benchmark Example

Existing source entity from `packages.dataset_builder.models`.

**Fields used by this feature**:

- `example_id`: stable semantic source identifier.
- `audio_id`: stable audio artifact identifier.
- `dataset_version`: source text dataset version.
- `language`: source language, including English and Russian.
- `split`: deterministic train, validation, or test split.
- `text`: transcript passed to synthesis and stored as reference transcript.
- Existing benchmark labels: preserved for downstream model evaluation.

**Validation rules**:

- Must have non-empty text before real synthesis.
- Must have unique output audio paths within one generation run.
- Split, language, and dataset version must be copied unchanged to audio
  records.

## Synthesis Settings

Configuration for fixture or Piper audio generation.

**Fields**:

- `engine`: `fixture-silent` for CI fixtures or `piper` for real Piper audio.
- `sample_rate_hz`: output sample rate reported in metadata.
- `duration_ms`: known duration for fixture output; optional or derived for
  Piper output.
- `channels`: output channel count when known.
- `sample_width_bytes`: output sample width when known.
- `voice`: logical voice name used for metadata and summaries.
- `voice_model_path`: local Piper `.onnx` model path for real synthesis.
- `voice_config_path`: local Piper `.onnx.json` config path when separate from
  the model path.
- `voice_by_language`: optional language-to-voice mapping for bilingual runs.
- `sentence_silence`, `length_scale`, `noise_scale`, `noise_w_scale`: optional
  Piper synthesis controls when exposed.

**Validation rules**:

- `engine="piper"` requires usable local voice resources before synthesis.
- Default Piper settings must resolve to concrete local voice resources before
  synthesis starts.
- Piper mode must fail if the package or voice files are unavailable.
- Fixture mode remains deterministic and does not require external resources.

## Audio Dataset Record

Existing `AudioExample` record written to audio metadata JSONL.

**Fields**:

- `audio_id`: generated audio artifact identifier.
- `example_id`: source text example identifier.
- `dataset_version`: source dataset version.
- `language`: source language.
- `split`: source split.
- `reference_transcript`: text used for synthesis.
- `audio_path`: generated WAV path.
- `tts_engine`: synthesis engine used.
- `voice`: selected voice name or path label.
- `sample_rate_hz`: sample rate reported for the audio file.
- `duration_ms`: duration when known or derived from the WAV file.
- `synthesis_settings`: generation configuration used for the record.

**Validation rules**:

- Must reference an existing source example.
- Must point to a generated WAV file after a successful run.
- Must not report `fixture-silent` when Piper mode was requested.

## Generation Run

Logical operation that creates a complete audio dataset from source examples.

**States**:

- `not_started`: no synthesis attempted.
- `synthesizing`: examples are being converted to audio.
- `complete`: all requested examples have WAV files and metadata records.
- `failed`: generation stopped because input, output path, package, voice, or
  synthesis failed.

**Validation rules**:

- A complete metadata manifest is written only for `complete`.
- Failures include the affected example when synthesis fails after run start.
- Output collisions fail before overwriting unrelated files unless explicitly
  allowed by the future implementation.
