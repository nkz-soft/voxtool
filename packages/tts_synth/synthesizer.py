from __future__ import annotations

import wave
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Protocol

from packages.dataset_builder.models import BenchmarkExample, Language
from packages.tts_synth.models import AudioExample, SynthesisSettings


class SynthesisError(RuntimeError):
    """Raised when audio generation cannot produce a complete dataset."""


class SynthesisResourceError(SynthesisError):
    """Raised when the selected synthesis engine or voice resources are unavailable."""


class SynthesizerBackend(Protocol):
    """Common interface for benchmark input audio synthesizers."""

    settings: SynthesisSettings

    def synthesize(self, example: BenchmarkExample, output_dir: Path) -> AudioExample:
        """Write an audio file for one example and return linked metadata."""


class FixtureSynthesizer:
    """Create deterministic silent WAV fixtures for benchmark audio metadata."""

    def __init__(self, settings: SynthesisSettings | None = None) -> None:
        """Initialize the synthesizer with deterministic output settings."""
        self.settings = settings or SynthesisSettings()

    def synthesize(self, example: BenchmarkExample, output_dir: Path) -> AudioExample:
        """Write a silent WAV file and return linked audio metadata."""
        output_dir.mkdir(parents=True, exist_ok=True)
        audio_path = output_dir / f"{example.audio_id}.wav"
        frame_count = (self.settings.sample_rate_hz * self.settings.duration_ms) // 1000
        zero_frame = b"\x00" * self.settings.sample_width_bytes
        frames = zero_frame * frame_count * self.settings.channels

        with wave.open(str(audio_path), "wb") as wav_file:
            wav_file.setnchannels(self.settings.channels)
            wav_file.setsampwidth(self.settings.sample_width_bytes)
            wav_file.setframerate(self.settings.sample_rate_hz)
            wav_file.writeframes(frames)

        return AudioExample.from_benchmark_example(
            example,
            audio_path=audio_path,
            settings=self.settings,
            duration_ms=self.settings.duration_ms,
        )


class PiperSynthesizer:
    """Create real Piper TTS WAV samples for benchmark audio metadata."""

    def __init__(self, settings: SynthesisSettings) -> None:
        """Initialize the Piper synthesizer with local voice settings."""
        self.settings = settings
        self._voice_cache: dict[tuple[Path, Path | None], Any] = {}

    def synthesize(self, example: BenchmarkExample, output_dir: Path) -> AudioExample:
        """Write a Piper WAV file and return linked audio metadata."""
        output_dir.mkdir(parents=True, exist_ok=True)
        audio_path = output_dir / f"{example.audio_id}.wav"
        model_path, config_path, voice_name = _voice_resources_for_language(
            self.settings,
            example.language,
        )
        voice = self._voice_for(model_path, config_path)

        try:
            with wave.open(str(audio_path), "wb") as wav_file:
                _synthesize_piper_voice(
                    voice,
                    example.text,
                    wav_file,
                    self.settings,
                )
        except SynthesisError:
            raise
        except Exception as exc:
            if audio_path.exists():
                audio_path.unlink()
            raise SynthesisError(
                f"Piper synthesis failed for example {example.example_id}: {exc}"
            ) from exc

        sample_rate_hz, duration_ms = _wav_metadata(audio_path)
        return AudioExample.from_benchmark_example(
            example,
            audio_path=audio_path,
            settings=self.settings.model_copy(
                update={"sample_rate_hz": sample_rate_hz}
            ),
            duration_ms=duration_ms,
            voice=voice_name,
        )

    def _voice_for(self, model_path: Path, config_path: Path | None) -> Any:
        cache_key = (model_path, config_path)
        if cache_key not in self._voice_cache:
            self._voice_cache[cache_key] = _load_piper_voice(model_path, config_path)
        return self._voice_cache[cache_key]


def _load_piper_voice(model_path: Path, config_path: Path | None = None) -> Any:
    """Load a Piper voice lazily so default CI does not require `piper-tts`."""
    try:
        from piper.voice import PiperVoice  # type: ignore[import-not-found]
    except ImportError as exc:
        raise SynthesisResourceError(
            "piper-tts is not installed; install the optional speech dependencies"
        ) from exc

    try:
        if config_path is not None:
            return PiperVoice.load(str(model_path), config_path=str(config_path))
        return PiperVoice.load(str(model_path))
    except TypeError:
        if config_path is not None:
            return PiperVoice.load(str(model_path), str(config_path))
        return PiperVoice.load(str(model_path))


def _synthesize_piper_voice(
    voice: Any,
    text: str,
    wav_file: wave.Wave_write,
    settings: SynthesisSettings,
) -> None:
    kwargs = {
        key: value
        for key, value in {
            "sentence_silence": settings.sentence_silence,
            "length_scale": settings.length_scale,
            "noise_scale": settings.noise_scale,
            "noise_w_scale": settings.noise_w_scale,
        }.items()
        if value is not None
    }
    if hasattr(voice, "synthesize_wav"):
        voice.synthesize_wav(text, wav_file, **kwargs)
        return
    if hasattr(voice, "synthesize"):
        voice.synthesize(text, wav_file, **kwargs)
        return
    raise SynthesisResourceError("Loaded Piper voice does not expose synthesis methods")


def _voice_resources_for_language(
    settings: SynthesisSettings,
    language: Language,
) -> tuple[Path, Path | None, str]:
    model_path = settings.voice_model_path_by_language.get(language)
    if model_path is None:
        model_path = settings.voice_model_path
    if model_path is None:
        raise SynthesisResourceError(
            f"Piper voice model path is required for language {language}"
        )
    if not model_path.exists():
        raise SynthesisResourceError(f"Piper voice model not found: {model_path}")

    config_path = settings.voice_config_path_by_language.get(language)
    if config_path is None:
        config_path = settings.voice_config_path
    if config_path is not None and not config_path.exists():
        raise SynthesisResourceError(f"Piper voice config not found: {config_path}")

    voice_name = settings.voice_by_language.get(language) or settings.voice
    return model_path, config_path, voice_name or model_path.stem


def _wav_metadata(audio_path: Path) -> tuple[int, int]:
    with wave.open(str(audio_path), "rb") as wav_file:
        sample_rate_hz = wav_file.getframerate()
        frame_count = wav_file.getnframes()
    duration_ms = round((frame_count / sample_rate_hz) * 1000)
    return sample_rate_hz, max(duration_ms, 1)


def _validate_examples_for_engine(
    examples: list[BenchmarkExample],
    *,
    output_dir: Path,
    settings: SynthesisSettings,
) -> None:
    seen_paths: set[Path] = set()
    for example in examples:
        if not example.text.strip():
            raise SynthesisError(f"Example {example.example_id} has blank text")
        audio_path = output_dir / f"{example.audio_id}.wav"
        if audio_path in seen_paths:
            raise SynthesisError(f"Duplicate audio output path: {audio_path}")
        seen_paths.add(audio_path)
        if settings.engine == "piper" and audio_path.exists():
            raise SynthesisError(f"Audio output already exists: {audio_path}")


def _backend_for_settings(settings: SynthesisSettings | None) -> SynthesizerBackend:
    resolved = settings or SynthesisSettings()
    if resolved.engine == "fixture-silent":
        return FixtureSynthesizer(settings=resolved)
    if resolved.engine == "piper":
        return PiperSynthesizer(settings=resolved)
    raise SynthesisError(f"Unsupported TTS engine: {resolved.engine}")


def synthesize_dataset(
    examples: Iterable[BenchmarkExample],
    *,
    output_dir: Path,
    settings: SynthesisSettings | None = None,
) -> list[AudioExample]:
    """Synthesize one complete audio dataset with the selected TTS backend."""
    example_list = list(examples)
    synthesizer = _backend_for_settings(settings)
    _validate_examples_for_engine(
        example_list,
        output_dir=output_dir,
        settings=synthesizer.settings,
    )
    return [synthesizer.synthesize(example, output_dir) for example in example_list]
