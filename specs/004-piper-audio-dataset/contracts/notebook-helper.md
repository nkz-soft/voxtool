# Contract: Notebook Helper

## Function

```python
audio_dataset = demo.demo_dataset()
audio_examples = demo.synthesize_demo_audio(audio_dataset, output_dir="demo_audio")
```

## Required Behavior

- The high-level call pattern remains valid.
- The helper generates an audio dataset from the provided benchmark examples.
- The default behavior for user-facing demo audio uses Piper TTS when the
  required speech dependencies and voice resources are configured.
- When no explicit synthesis settings are passed, the helper resolves Piper
  voice resources from documented local configuration and fails clearly if they
  are missing.
- Users can still pass explicit synthesis settings for fixture or alternate
  bounded test behavior.
- Returned `AudioExample` records can be passed directly to `run_audio_demo`.

## Failure Behavior

- Piper resource failures raise a clear exception before returning a misleading
  complete dataset.
- Partial synthesis is not reported as a successful complete dataset.
- The helper does not upload user text or audio to external services.
