# Contract: Audio CLI

## Command

`python scripts/synthesize_audio.py --dataset <dataset.jsonl> --output <dir>`

The existing command remains valid. The CLI defaults to `fixture-silent` for
bounded local and CI use. Users request real demo audio by passing
`--engine piper` with configured voice resources.

## Piper Mode

Additional CLI behavior:

```text
python scripts/synthesize_audio.py \
  --dataset data/fixtures/examples.small.jsonl \
  --output demo_audio \
  --engine piper \
  --voice ru_RU-irina-medium \
  --voice-model-path model-files/piper/ru_RU-irina-medium.onnx \
  --voice-config-path model-files/piper/ru_RU-irina-medium.onnx.json
```

Fixture mode for bounded CI:

```text
python scripts/synthesize_audio.py \
  --dataset data/fixtures/examples.small.jsonl \
  --output .tmp/audio-fixture-check \
  --engine fixture-silent
```

## Required Behavior

- Reads benchmark examples from dataset JSONL.
- Generates one WAV file per input example.
- Writes `audio.jsonl` only when all requested examples are generated.
- Preserves source example IDs, dataset version, language, split, transcript,
  and synthesis metadata.
- Fails clearly when Piper is requested but the package or voice resources are
  unavailable.
- Does not download voice models implicitly.

## CI Behavior

- Default fixture mode remains usable in ordinary CI.
- Piper mode can be tested with mocks and resource validation without requiring
  real voice downloads.
