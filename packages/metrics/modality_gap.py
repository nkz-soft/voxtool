from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence

from packages.metrics.tool_use import ToolUseEvaluation, tool_call_exact_match_rate

MetricFunction = Callable[[Sequence[ToolUseEvaluation]], float]


def paired_example_ids(
    text_evaluations: Iterable[ToolUseEvaluation],
    audio_evaluations: Iterable[ToolUseEvaluation],
) -> set[str]:
    """Return example IDs evaluated in both the text and audio runs."""
    text_ids = {item.example_id for item in text_evaluations}
    audio_ids = {item.example_id for item in audio_evaluations}
    return text_ids & audio_ids


def modality_gap(
    text_evaluations: Sequence[ToolUseEvaluation],
    audio_evaluations: Sequence[ToolUseEvaluation],
    metric: MetricFunction = tool_call_exact_match_rate,
) -> float | None:
    """Compute text-minus-audio metric difference over paired example IDs.

    Returns None when the runs share no example IDs, so unpaired runs never
    report a misleading zero gap.
    """
    shared_ids = paired_example_ids(text_evaluations, audio_evaluations)
    if not shared_ids:
        return None
    paired_text = [item for item in text_evaluations if item.example_id in shared_ids]
    paired_audio = [item for item in audio_evaluations if item.example_id in shared_ids]
    return metric(paired_text) - metric(paired_audio)
