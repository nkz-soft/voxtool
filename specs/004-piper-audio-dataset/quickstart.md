# Quickstart: Piper Audio Dataset

## Ordinary CI Validation

Run the bounded validation path without real Piper assets:

```powershell
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run python -m pytest
uv run python scripts/synthesize_audio.py --dataset data/fixtures/examples.small.jsonl --output .tmp/audio-fixture-check --engine fixture-silent
```

Expected result: tests pass and fixture audio metadata is generated without
installing the optional speech dependency group.

## Manual Piper Setup

Install the optional speech dependencies:

```powershell
uv sync --group speech
```

Download Piper voice files outside Git, for example under `model-files/piper/`.
Each voice needs a `.onnx` model file and matching `.onnx.json` config file.
Review the voice model license before using it in benchmark artifacts.

For the notebook helper default path, configure local Piper resources with
environment variables before calling `demo.synthesize_demo_audio(...)`:

```powershell
$env:VOXTOOL_PIPER_VOICE = "ru_RU-irina-medium"
$env:VOXTOOL_PIPER_VOICE_MODEL = "model-files/piper/ru_RU-irina-medium.onnx"
$env:VOXTOOL_PIPER_VOICE_CONFIG = "model-files/piper/ru_RU-irina-medium.onnx.json"
```

For bilingual voice selection, provide language-specific overrides:

```powershell
$env:VOXTOOL_PIPER_VOICE_RU = "ru_RU-irina-medium"
$env:VOXTOOL_PIPER_VOICE_MODEL_RU = "model-files/piper/ru_RU-irina-medium.onnx"
$env:VOXTOOL_PIPER_VOICE_CONFIG_RU = "model-files/piper/ru_RU-irina-medium.onnx.json"
$env:VOXTOOL_PIPER_VOICE_EN = "en_US-lessac-medium"
$env:VOXTOOL_PIPER_VOICE_MODEL_EN = "model-files/piper/en_US-lessac-medium.onnx"
$env:VOXTOOL_PIPER_VOICE_CONFIG_EN = "model-files/piper/en_US-lessac-medium.onnx.json"
```

Suggested bounded bilingual validation:

```powershell
uv run python scripts/synthesize_audio.py `
  --dataset data/fixtures/examples.small.jsonl `
  --output demo_audio `
  --engine piper `
  --voice ru_RU-irina-medium `
  --voice-model-path model-files/piper/ru_RU-irina-medium.onnx `
  --voice-config-path model-files/piper/ru_RU-irina-medium.onnx.json
```

For an English and Russian voice split, use the language-specific voice mapping
added by implementation tasks once available.

## Notebook Flow

The user-facing helper stays concise:

```python
audio_dataset = demo.demo_dataset()
audio_examples = demo.synthesize_demo_audio(audio_dataset, output_dir="demo_audio")
```

After generation:

```python
demo.audio_summary(audio_examples)
demo.run_audio_demo(adapter, audio_examples)
```

## PR Evidence

Include these in the pull request:

- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run mypy .`
- `uv run python -m pytest`
- Fixture synthesis command output path
- Manual Piper synthesis artifact path when real voice resources are available,
  or a skipped-resource note if local Piper voice files are unavailable

Current implementation validation note: manual real Piper synthesis was skipped
because no local Piper `.onnx` voice files were available in the workspace.
Fixture synthesis evidence: `.tmp/audio-fixture-check/audio.jsonl`.
