# Audio Fixture Notes

Phase 6 uses deterministic silent WAV files generated during tests instead of
checking binary audio into the repository. The generated metadata records point
to local `.wav` artifacts and preserve `audio_id`, `example_id`, split,
reference transcript, and synthesis settings for each source dataset example.

Real Piper TTS voices are manual artifacts and stay outside Git. Put downloaded
`.onnx` and matching `.onnx.json` files under an ignored location such as
`model-files/piper/`, then point the CLI or notebook environment at them with
`--voice-model-path` / `--voice-config-path` or `VOXTOOL_PIPER_VOICE_MODEL` /
`VOXTOOL_PIPER_VOICE_CONFIG`. Review each voice license before using generated
audio as benchmark evidence.
