from __future__ import annotations

import re

_PUNCTUATION_RE = re.compile(r"[^\w\s]", flags=re.UNICODE)
_WHITESPACE_RE = re.compile(r"\s+")


def normalize_transcript(transcript: str) -> str:
    """Normalize English and Russian transcripts before ASR metric calculation."""
    without_punctuation = _PUNCTUATION_RE.sub(" ", transcript.casefold())
    return _WHITESPACE_RE.sub(" ", without_punctuation).strip()
