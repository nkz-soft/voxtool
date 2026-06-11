import pytest
from packages.asr_eval.normalization import normalize_transcript
from packages.asr_eval.wer import calculate_wer


def test_normalize_transcript_handles_english_case_punctuation_and_spacing() -> None:
    assert normalize_transcript("  Convert, TWO kilometers to meters!  ") == (
        "convert two kilometers to meters"
    )


def test_normalize_transcript_handles_russian_case_punctuation_and_spacing() -> None:
    assert normalize_transcript("  Переведи  ДВА километра, в метры!  ") == (
        "переведи два километра в метры"
    )


def test_calculate_wer_uses_normalized_english_transcripts() -> None:
    assert calculate_wer(
        "Convert two kilometers to meters.",
        "convert two kilometers",
    ) == pytest.approx(0.4)


def test_calculate_wer_uses_normalized_russian_transcripts() -> None:
    assert calculate_wer("Переведи два километра в метры.", "переведи два метра") == (
        pytest.approx(0.6)
    )
