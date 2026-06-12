from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
from apps.cli.__main__ import app
from packages.dataset_builder.io import write_jsonl as write_dataset_jsonl
from packages.dataset_builder.models import BenchmarkExample
from packages.pipeline_runner.artifacts import PipelineRunRecord, write_pipeline_jsonl
from packages.report_builder.report import build_report, select_best_pipeline
from packages.tool_schema import ToolInvocation
from packages.tool_schema.models import ToolArguments, Unit
from typer.testing import CliRunner

SUMMARY_COLUMNS = [
    "run_id",
    "pipeline",
    "split",
    "language",
    "parsable_tool_invocation_rate",
    "repair_success_rate",
    "tool_decision_accuracy",
    "tool_call_exact_match",
    "argument_value_match",
    "argument_from_unit_match",
    "argument_to_unit_match",
    "precision",
    "recall",
    "false_alarm_rate",
    "wer",
    "modality_gap",
]

REQUIRED_SECTIONS = [
    "## Dataset Summary",
    "## Per-Pipeline Metrics",
    "## Language Splits",
    "## Confusion Matrix",
    "## ASR WER",
    "## Modality Gap",
    "## Best Pipeline",
    "## Failure Cases",
]


def _examples() -> list[BenchmarkExample]:
    tool_call = ToolInvocation(
        tool="units.convert",
        arguments=ToolArguments(
            value=2,
            from_unit=Unit.KILOMETER,
            to_unit=Unit.METER,
        ),
    )
    return [
        BenchmarkExample(
            example_id="v1-en-length-0001",
            dataset_version="v1",
            language="en",
            split="test",
            unit_family="length",
            text="Convert 2 kilometers to meters.",
            needs_tool=True,
            expected_tool_call=tool_call,
            expected_final_answer="2 kilometers is 2000 meters.",
            audio_id="v1-en-length-0001-audio",
        ),
        BenchmarkExample(
            example_id="v1-ru-none-0001",
            dataset_version="v1",
            language="ru",
            split="test",
            unit_family="none",
            text="Скажи привет.",
            needs_tool=False,
            expected_tool_call=None,
            expected_final_answer="Привет.",
            audio_id="v1-ru-none-0001-audio",
        ),
    ]


def _parsed_output(*, needs_tool: bool, value: float = 2) -> dict[str, Any]:
    tool_call = None
    if needs_tool:
        tool_call = {
            "tool": "units.convert",
            "arguments": {
                "value": value,
                "from_unit": "kilometer",
                "to_unit": "meter",
            },
        }
    return {
        "needs_tool": needs_tool,
        "tool_call": tool_call,
        "final_answer": "2 kilometers is 2000 meters.",
    }


def _records() -> dict[str, list[PipelineRunRecord]]:
    pipeline_a = [
        PipelineRunRecord(
            run_id="smoke-009",
            pipeline="A",
            example_id="v1-en-length-0001",
            dataset_version="v1",
            model_adapter="MockModelAdapter",
            input_modality="text",
            raw_output="{}",
            parsed_output=_parsed_output(needs_tool=True),
            first_pass_parsable=True,
            repair_attempted=False,
            repair_success=False,
        ),
        PipelineRunRecord(
            run_id="smoke-009",
            pipeline="A",
            example_id="v1-ru-none-0001",
            dataset_version="v1",
            model_adapter="MockModelAdapter",
            input_modality="text",
            raw_output="{}",
            parsed_output=_parsed_output(needs_tool=False),
            first_pass_parsable=True,
            repair_attempted=False,
            repair_success=False,
        ),
    ]
    pipeline_b = [
        PipelineRunRecord(
            run_id="smoke-009",
            pipeline="B",
            example_id="v1-en-length-0001",
            dataset_version="v1",
            model_adapter="MockModelAdapter",
            input_modality="audio",
            raw_output="{}",
            parsed_output=_parsed_output(needs_tool=True, value=999),
            first_pass_parsable=True,
            repair_attempted=False,
            repair_success=False,
            transcript="Convert 2 kilometers to meters.",
            wer=0.25,
        ),
        PipelineRunRecord(
            run_id="smoke-009",
            pipeline="B",
            example_id="v1-ru-none-0001",
            dataset_version="v1",
            model_adapter="MockModelAdapter",
            input_modality="audio",
            raw_output="not json",
            parsed_output=None,
            first_pass_parsable=False,
            repair_attempted=True,
            repair_success=False,
            transcript="Скажи привет.",
            wer=0.0,
        ),
    ]
    return {"A": pipeline_a, "B": pipeline_b}


def test_build_report_contains_all_contract_sections() -> None:
    report = build_report(dataset=_examples(), records_by_pipeline=_records())

    for section in REQUIRED_SECTIONS:
        assert section in report, f"missing section: {section}"
    # Failure analysis must categorize the wrong value and the failed repair.
    assert "numeric_value" in report
    assert "repair_failed" in report


def test_select_best_pipeline_returns_pipeline_and_rationale() -> None:
    best = select_best_pipeline(
        dataset=_examples(),
        records_by_pipeline=_records(),
    )

    assert best.pipeline == "A"
    assert best.rationale


def test_report_cli_writes_report_summary_and_plots(tmp_path: Path) -> None:
    dataset_path = tmp_path / "dataset.jsonl"
    write_dataset_jsonl(dataset_path, _examples())
    records = _records()
    run_a = tmp_path / "pipeline-a.jsonl"
    run_b = tmp_path / "pipeline-b.jsonl"
    write_pipeline_jsonl(run_a, records["A"])
    write_pipeline_jsonl(run_b, records["B"])
    report_path = tmp_path / "reports" / "report.md"
    summary_path = tmp_path / "reports" / "summary.csv"
    plots_dir = tmp_path / "reports" / "plots"

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "report",
            "build",
            "--dataset",
            str(dataset_path),
            "--run",
            str(run_a),
            "--run",
            str(run_b),
            "--output",
            str(report_path),
            "--summary",
            str(summary_path),
            "--plots-dir",
            str(plots_dir),
        ],
    )

    assert result.exit_code == 0, result.output
    report = report_path.read_text(encoding="utf-8")
    for section in REQUIRED_SECTIONS:
        assert section in report, f"missing section: {section}"

    summary = pd.read_csv(summary_path)
    assert list(summary.columns) == SUMMARY_COLUMNS
    assert set(summary["pipeline"]) == {"A", "B"}
    assert list(plots_dir.glob("*.png"))


def test_build_report_script_entrypoint(tmp_path: Path) -> None:
    import subprocess
    import sys

    dataset_path = tmp_path / "dataset.jsonl"
    write_dataset_jsonl(dataset_path, _examples())
    run_a = tmp_path / "pipeline-a.jsonl"
    write_pipeline_jsonl(run_a, _records()["A"])
    report_path = tmp_path / "report.md"
    summary_path = tmp_path / "summary.csv"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_report.py",
            "--dataset",
            str(dataset_path),
            "--run",
            str(run_a),
            "--output",
            str(report_path),
            "--summary",
            str(summary_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "## Best Pipeline" in report_path.read_text(encoding="utf-8")
    assert summary_path.exists()


def test_summary_supports_parquet_output(tmp_path: Path) -> None:
    import pytest

    pytest.importorskip("pyarrow")

    from packages.metrics.aggregation import summarize_metrics, write_summary

    dataset = _examples()
    summary = summarize_metrics(dataset=dataset, records_by_pipeline=_records())
    parquet_path = tmp_path / "summary.parquet"
    write_summary(summary, parquet_path)

    loaded = pd.read_parquet(parquet_path)
    assert list(loaded.columns) == SUMMARY_COLUMNS


def test_pipeline_records_round_trip_for_report_inputs(tmp_path: Path) -> None:
    path = tmp_path / "pipeline-a.jsonl"
    write_pipeline_jsonl(path, _records()["A"])

    lines = path.read_text(encoding="utf-8").splitlines()
    parsed = [json.loads(line) for line in lines]

    assert len(parsed) == 2
    assert parsed[0]["pipeline"] == "A"
