from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pandas as pd
from packages.dataset_builder.models import BenchmarkExample, Language
from packages.metrics.tool_use import (
    ToolUseEvaluation,
    confusion_matrix,
    evaluate_run,
    false_alarm_rate,
    parsability_rate,
    precision,
    recall,
    tool_call_exact_match_rate,
    tool_decision_accuracy,
)
from packages.model_runner.adapters.base import ModelAdapter
from packages.model_runner.adapters.mock import MockModelAdapter
from packages.model_runner.asr import ASRAdapter, MockASRAdapter
from packages.model_runner.registry import available_adapters, build_adapter
from packages.pipeline_runner.artifacts import PipelineRunRecord
from packages.pipeline_runner.capabilities import check_adapter_for_pipeline
from packages.pipeline_runner.pipeline_a import run_pipeline_a
from packages.pipeline_runner.pipeline_c import run_pipeline_c
from packages.pipeline_runner.pipeline_d import run_pipeline_d
from packages.pipeline_runner.runner import _AdapterBridge
from packages.tool_schema.models import ToolArguments, ToolInvocation, Unit
from packages.tool_schema.providers import ToolExecutor
from packages.tool_schema.units import default_tool_registry
from packages.tts_synth.models import AudioExample, SynthesisSettings
from packages.tts_synth.synthesizer import synthesize_dataset

# Stable list of adapters a Colab user can select in the demo notebook. The mock
# adapter requires no download and runs anywhere; the real adapters fetch weights
# lazily on first use and need GPU/Colab resources.
SELECTABLE_ADAPTERS: tuple[str, ...] = tuple(available_adapters())


def list_adapters() -> list[str]:
    """Return adapter IDs the Colab demo can select."""
    return list(SELECTABLE_ADAPTERS)


def select_adapter(
    adapter_id: str, *, config_path: str | Path | None = None
) -> ModelAdapter:
    """Build an import-safe adapter by ID for the notebook.

    No model is downloaded here; real weights load lazily on the first text run.
    """
    return build_adapter(adapter_id, config_path=config_path)


def text_examples(prompts: list[str]) -> list[BenchmarkExample]:
    """Wrap raw demo prompts as Pipeline A benchmark examples.

    Demo prompts carry no expected label, so each example is marked as not
    needing a tool; the adapter's actual tool decision is still recorded by the
    pipeline run.
    """
    examples: list[BenchmarkExample] = []
    for index, prompt in enumerate(prompts, start=1):
        example_id = f"demo-{index:04d}"
        examples.append(
            BenchmarkExample(
                example_id=example_id,
                dataset_version="demo",
                language="en",
                split="test",
                unit_family="none",
                text=prompt,
                needs_tool=False,
                expected_tool_call=None,
                expected_final_answer="(demo)",
                audio_id=f"{example_id}-audio",
            )
        )
    return examples


# Curated, labeled demo examples per language. Unlike free-form prompts, each
# carries an expected tool decision and (when applicable) an expected tool call,
# so the tool-use metrics (decision accuracy, exact match, precision/recall) are
# meaningful and comparable across models and languages. The conversion prompts
# use phrasing the deterministic mock recognizes in both English and Russian, so
# a no-download mock run scores well and exercises the full path for each
# language.
DEMO_LANGUAGES: tuple[Language, ...] = ("en", "ru")

# (text, value, from_unit, to_unit, unit_family) for tool examples.
_DEMO_TOOL_SPECS: dict[Language, tuple[tuple[str, float, Unit, Unit, str], ...]] = {
    "en": (
        ("Convert 2 kilometers to meters.", 2, Unit.KILOMETER, Unit.METER, "length"),
        ("Convert 500 grams to kilograms.", 500, Unit.GRAM, Unit.KILOGRAM, "mass"),
        ("Convert 5 pounds to ounces.", 5, Unit.POUND, Unit.OUNCE, "mass"),
    ),
    "ru": (
        ("Сконвертируй 2 километра в метры.", 2, Unit.KILOMETER, Unit.METER, "length"),
        ("Переведи 500 граммов в килограммы.", 500, Unit.GRAM, Unit.KILOGRAM, "mass"),
        ("Переведи 5 фунтов в унции.", 5, Unit.POUND, Unit.OUNCE, "mass"),
    ),
}
_DEMO_NO_TOOL_PROMPTS: dict[Language, tuple[str, ...]] = {
    "en": (
        "What is the capital of France?",
        "Who wrote the play Hamlet?",
    ),
    "ru": (
        "Какая столица Франции?",
        "Кто написал пьесу «Гамлет»?",
    ),
}


def demo_dataset(
    languages: Sequence[Language] = DEMO_LANGUAGES,
) -> list[BenchmarkExample]:
    """Return a small labeled dataset mixing tool and no-tool examples.

    Bilingual by default (English and Russian) so models can be compared per
    language. The labels let the comparison metrics score each model's tool
    decisions and argument extraction, not just parsability. Pass this to
    :func:`compare_models` to benchmark several adapters on the same examples.
    """
    examples: list[BenchmarkExample] = []
    for language in languages:
        index = 0
        for prompt, value, from_unit, to_unit, family in _DEMO_TOOL_SPECS[language]:
            index += 1
            example_id = f"demo-{language}-{index:04d}"
            examples.append(
                BenchmarkExample(
                    example_id=example_id,
                    dataset_version="demo",
                    language=language,
                    split="test",
                    unit_family=family,  # type: ignore[arg-type]
                    text=prompt,
                    needs_tool=True,
                    expected_tool_call=ToolInvocation(
                        tool="units.convert",
                        arguments=ToolArguments(
                            value=value, from_unit=from_unit, to_unit=to_unit
                        ),
                    ),
                    expected_final_answer="(demo)",
                    audio_id=f"{example_id}-audio",
                )
            )
        for prompt in _DEMO_NO_TOOL_PROMPTS[language]:
            index += 1
            example_id = f"demo-{language}-{index:04d}"
            examples.append(
                BenchmarkExample(
                    example_id=example_id,
                    dataset_version="demo",
                    language=language,
                    split="test",
                    unit_family="none",
                    text=prompt,
                    needs_tool=False,
                    expected_tool_call=None,
                    expected_final_answer="(demo)",
                    audio_id=f"{example_id}-audio",
                )
            )
    return examples


def run_examples(
    adapter: ModelAdapter,
    examples: Sequence[BenchmarkExample],
    *,
    run_id: str = "colab-demo",
    output_path: Path | None = None,
) -> list[PipelineRunRecord]:
    """Run Pipeline A over labeled examples with the selected adapter.

    Records preserve raw output, parsed JSON, validation results, tool execution
    results, and final answers exactly like a normal benchmark run.
    """
    registry = default_tool_registry()
    executor = ToolExecutor(registry)
    skip = check_adapter_for_pipeline(adapter, "A")
    if skip is not None:
        raise ValueError(skip.reason)
    return run_pipeline_a(
        list(examples),
        run_id=run_id,
        model_adapter=_AdapterBridge(adapter),
        registry=registry,
        executor=executor,
        output_path=output_path,
    )


def run_text_demo(
    adapter: ModelAdapter,
    prompts: list[str],
    *,
    run_id: str = "colab-demo",
    output_path: Path | None = None,
) -> list[PipelineRunRecord]:
    """Run Pipeline A over free-form demo prompts with the selected adapter.

    Prompts carry no expected label; for scored cross-model comparison use
    :func:`demo_dataset` with :func:`compare_models` instead.
    """
    return run_examples(
        adapter,
        text_examples(prompts),
        run_id=run_id,
        output_path=output_path,
    )


def synthesize_demo_audio(
    examples: Sequence[BenchmarkExample],
    *,
    output_dir: str | Path = "demo_audio",
    settings: SynthesisSettings | None = None,
) -> list[AudioExample]:
    """Generate deterministic test audio from example text instead of uploading.

    Uses the local fixture-silent TTS engine, so no upload, cloud service, or
    model download is required. Each returned :class:`AudioExample` carries the
    source text as its reference transcript plus a path to a generated WAV file,
    and can be fed straight into :func:`run_audio_demo`.
    """
    settings = settings or SynthesisSettings(engine="fixture-silent")
    return synthesize_dataset(
        list(examples), output_dir=Path(output_dir), settings=settings
    )


def audio_summary(audio_examples: Sequence[AudioExample]) -> list[dict[str, Any]]:
    """Flatten synthesized audio metadata into the fields the notebook displays."""
    return [
        {
            "audio_id": audio.audio_id,
            "example_id": audio.example_id,
            "reference_transcript": audio.reference_transcript,
            "audio_path": audio.audio_path,
            "duration_ms": audio.duration_ms,
            "tts_engine": audio.tts_engine,
        }
        for audio in audio_examples
    ]


def run_audio_demo(
    adapter: ModelAdapter,
    audio_examples: Sequence[AudioExample],
    *,
    run_id: str = "colab-audio-demo",
    asr_adapter: ASRAdapter | None = None,
    output_path: Path | None = None,
) -> list[PipelineRunRecord]:
    """Run an audio tool-calling pipeline over synthesized audio examples.

    Picks Pipeline C (direct audio in) when the adapter declares audio input,
    such as Voxtral; otherwise falls back to Pipeline D (cascaded ASR then text
    tool-calling), which works with text-only adapters like the mock by using a
    deterministic mock ASR. Raises when the adapter supports neither pipeline.
    """
    registry = default_tool_registry()
    executor = ToolExecutor(registry)
    bridge = _AdapterBridge(adapter)
    if check_adapter_for_pipeline(adapter, "C") is None:
        return run_pipeline_c(
            list(audio_examples),
            run_id=run_id,
            model_adapter=bridge,
            registry=registry,
            executor=executor,
            output_path=output_path,
        )
    skip = check_adapter_for_pipeline(adapter, "D")
    if skip is not None:
        raise ValueError(skip.reason)
    return run_pipeline_d(
        list(audio_examples),
        run_id=run_id,
        asr_adapter=asr_adapter or MockASRAdapter(),
        text_adapter=bridge,
        registry=registry,
        executor=executor,
        output_path=output_path,
    )


def demo_mock_adapter() -> MockModelAdapter:
    """Return the deterministic mock adapter for a no-download dry run."""
    return MockModelAdapter()


def _metrics_from_evaluations(
    evaluations: Sequence[ToolUseEvaluation],
) -> dict[str, Any]:
    """Aggregate one set of evaluations into the demo's metric fields."""
    matrix = confusion_matrix(evaluations)
    return {
        "examples": len(evaluations),
        "parsable_rate": parsability_rate(evaluations),
        "tool_decision_accuracy": tool_decision_accuracy(evaluations),
        "tool_call_exact_match": tool_call_exact_match_rate(evaluations),
        "precision": precision(matrix),
        "recall": recall(matrix),
        "false_alarm_rate": false_alarm_rate(matrix),
    }


def run_metrics(
    records: Sequence[PipelineRunRecord],
    dataset: Sequence[BenchmarkExample],
) -> dict[str, Any]:
    """Compute overall tool-use metrics for one model's run over the dataset.

    Scores parsability, tool decision accuracy, full tool-call exact match, and
    the decision precision/recall/false-alarm trade-off, mirroring the metrics
    the benchmark aggregation reports for the "all/all" subset.
    """
    return _metrics_from_evaluations(evaluate_run(list(records), list(dataset)))


def _language_metric_rows(
    records: Sequence[PipelineRunRecord],
    dataset: Sequence[BenchmarkExample],
) -> list[dict[str, Any]]:
    """Return per-language metric rows plus an overall ``all`` row."""
    evaluations = evaluate_run(list(records), list(dataset))
    languages = sorted({item.language for item in evaluations})
    rows: list[dict[str, Any]] = [
        {"language": "all", **_metrics_from_evaluations(evaluations)}
    ]
    for language in languages:
        subset = [item for item in evaluations if item.language == language]
        rows.append({"language": language, **_metrics_from_evaluations(subset)})
    return rows


def metrics_by_language(
    records: Sequence[PipelineRunRecord],
    dataset: Sequence[BenchmarkExample],
) -> pd.DataFrame:
    """Break one model's metrics down per language plus an overall ``all`` row.

    Lets the demo show, for example, how a model's Russian tool-calling compares
    with its English tool-calling on the same dataset.
    """
    return pd.DataFrame(_language_metric_rows(records, dataset))


def compare_models(
    adapter_ids: Sequence[str],
    dataset: Sequence[BenchmarkExample] | None = None,
    *,
    run_prefix: str = "colab-compare",
    config_paths: dict[str, str | Path] | None = None,
    by_language: bool = False,
) -> tuple[dict[str, list[PipelineRunRecord]], pd.DataFrame]:
    """Run several adapters over the same dataset and compare their metrics.

    Builds each adapter, runs Pipeline A over ``dataset`` (defaults to the
    bilingual :func:`demo_dataset`), and returns both the per-model run records
    and a comparison DataFrame with one row per model. With ``by_language=True``
    the table instead carries one row per (model, language) plus an ``all`` row
    per model, so English and Russian can be compared side by side. Real
    adapters (qwen/gemma/voxtral) fetch weights lazily on first use and need
    GPU/Colab resources; the mock adapter runs anywhere. An adapter that fails
    to run is recorded with an ``error`` column instead of aborting the whole
    comparison.
    """
    dataset = list(dataset) if dataset is not None else demo_dataset()
    config_paths = config_paths or {}
    records_by_model: dict[str, list[PipelineRunRecord]] = {}
    rows: list[dict[str, Any]] = []
    for adapter_id in adapter_ids:
        try:
            adapter = select_adapter(
                adapter_id, config_path=config_paths.get(adapter_id)
            )
            records = run_examples(
                adapter, dataset, run_id=f"{run_prefix}-{adapter_id}"
            )
            records_by_model[adapter_id] = records
            if by_language:
                entries = _language_metric_rows(records, dataset)
            else:
                entries = [run_metrics(records, dataset)]
            for entry in entries:
                rows.append({"model": adapter_id, **entry, "error": None})
        except Exception as exc:  # noqa: BLE001 - surface failures in the table
            rows.append({"model": adapter_id, "error": f"{type(exc).__name__}: {exc}"})
    return records_by_model, pd.DataFrame(rows)


def record_summary(record: PipelineRunRecord) -> dict[str, Any]:
    """Flatten one run record into the fields the notebook displays."""
    tool_result = record.tool_execution_result
    return {
        "example_id": record.example_id,
        "raw_output": record.raw_output,
        "parsable": record.first_pass_parsable,
        "validation_errors": record.validation_errors,
        "tool": tool_result.tool if tool_result is not None else None,
        "tool_result": tool_result.result if tool_result is not None else None,
        "final_answer": record.final_answer,
    }
