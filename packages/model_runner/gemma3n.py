from __future__ import annotations

from packages.tts_synth.models import AudioExample


class Gemma3nAdapter:
    """Placeholder interface for Gemma3n one-pass audio tool-calling.

    This adapter is a manual-run placeholder. Local inference is not
    implemented; attempting to generate audio output raises NotImplementedError.
    """

    name = "Gemma3nAdapter"

    def generate_audio(self, audio: AudioExample) -> None:
        """Generate audio tool-call output — not yet implemented for local runs."""
        raise NotImplementedError(
            "Gemma3nAdapter is a placeholder for manual Gemma3n local runs."
        )
