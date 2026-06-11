from __future__ import annotations

from jiwer import wer

from packages.asr_eval.normalization import normalize_transcript


def calculate_wer(reference: str, hypothesis: str) -> float:
    """Calculate word error rate after shared transcript normalization."""
    normalized_reference = normalize_transcript(reference)
    normalized_hypothesis = normalize_transcript(hypothesis)
    if not normalized_reference:
        return 0.0 if not normalized_hypothesis else 1.0
    return float(wer(normalized_reference, normalized_hypothesis))
