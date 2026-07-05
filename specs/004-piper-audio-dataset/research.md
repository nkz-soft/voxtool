# Research: Piper Audio Dataset

## Decision: Use Piper through optional `piper-tts` for real synthesis

**Rationale**: Piper is a local neural text-to-speech engine and the current
PyPI package is `piper-tts` 1.4.2. The upstream Python API supports loading a
voice with `PiperVoice.load(...)` and writing WAV output through
`synthesize_wav(...)`. This fits the existing package boundary because the
current `tts_synth` module already writes WAV files and returns `AudioExample`
metadata.

**Alternatives considered**:

- Shelling out to `python -m piper`: simpler to prototype, but slower for many
  examples because the CLI loads a voice model each invocation.
- Edge TTS: easier voice access, but online service behavior is less
  reproducible for benchmark input generation.
- Keep fixture-silent only: CI-friendly, but does not satisfy real model audio
  testing.

## Decision: Keep Piper in the optional `speech` dependency group

**Rationale**: The project already separates heavyweight audio/model
dependencies from default CI. `piper-tts` has binary wheels and voice model
artifacts that should not be required by ordinary CI. Implementation should use
lazy imports so default installs can still run tests, typecheck, and notebook
import checks without Piper installed.

**Alternatives considered**:

- Add Piper to default dependencies: rejected because ordinary CI should not
  depend on real TTS assets.
- Create a new dependency group: rejected because the existing `speech` group
  already covers optional speech/TTS dependencies.

## Decision: Use Piper mode without silent fallback

**Rationale**: The spec requires Piper TTS for real sample generation and clear
failure when synthesis resources are missing. The user-facing notebook helper
should use Piper when no alternate settings are provided. If Piper is selected,
missing package, voice model, or voice config should fail the run instead of
returning fixture-silent audio. CI and tests can select fixture-silent
explicitly.

**Alternatives considered**:

- Automatically fallback to fixture-silent: rejected because it would create
  misleading model-test evidence.
- Automatically download voices during synthesis: rejected for v1 because it
  makes generation less deterministic and can surprise CI/manual runs.

## Decision: Use local voice files and document manual download

**Rationale**: Piper voices consist of a `.onnx` model and `.onnx.json` config,
and voice model licensing can vary. Requiring local paths or a configured voice
directory keeps generation reproducible and forces users to manage voice assets
outside Git.

**Alternatives considered**:

- Commit small real voices: rejected because model files are large and
  licensing must be reviewed per voice.
- Download by voice name in every run: useful later, but v1 should be explicit
  and artifact-driven.

## Decision: Preserve current `AudioExample` compatibility

**Rationale**: Downstream audio pipelines already consume `AudioExample`. The
Piper implementation should continue to populate the existing fields and extend
`SynthesisSettings` only where needed for engine, voice, voice paths, and
optional Piper controls.

**Alternatives considered**:

- Introduce a parallel Piper metadata model: rejected because it would split
  pipeline compatibility and duplicate JSONL handling.

## Decision: Write complete manifests only after successful synthesis

**Rationale**: A partial manifest can look like a valid benchmark dataset. The
generation flow should synthesize all requested examples or report failure; if
metadata is written, it must represent the complete requested dataset.

**Alternatives considered**:

- Best-effort metadata with per-row failures: useful for diagnostics, but the
  spec requires incomplete generation not to be reported as complete.

## References

- Piper PyPI package: https://pypi.org/project/piper-tts/
- Piper upstream repository: https://github.com/OHF-Voice/piper1-gpl
- Piper Python API docs: https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/API_PYTHON.md
- Piper CLI docs: https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/CLI.md
- Piper voices docs: https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/VOICES.md
