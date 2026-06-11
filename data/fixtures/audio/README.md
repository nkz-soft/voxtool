# Audio Fixture Notes

Phase 6 uses deterministic silent WAV files generated during tests instead of
checking binary audio into the repository. The generated metadata records point
to local `.wav` artifacts and preserve `audio_id`, `example_id`, split,
reference transcript, and synthesis settings for each source dataset example.
