from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from packages.tool_schema.providers import (
    StructuredToolFailure,
    ToolManifest,
    ToolResult,
)


class SpeechOutputArtifact(BaseModel):
    """Optional final-answer speech output status attached to a pipeline run.

    ``generation_status`` distinguishes generated audio from intentionally
    ``disabled`` runs, capability ``skipped`` runs, and ``failed`` synthesis.
    A failure keeps the record (with no path) so it never erases tool-call
    metrics. Identity fields are optional so the same model serves both the
    embedded pipeline field and standalone speech manifests.
    """

    model_config = ConfigDict(extra="forbid")

    generation_status: Literal["generated", "disabled", "skipped", "failed"]
    speech_output_path: str | None = None
    speech_provider: str | None = None
    generation_error: str | None = None
    speech_output_id: str | None = None
    run_id: str | None = None
    example_id: str | None = None
    input_final_answer: str | None = None


class PipelineRunRecord(BaseModel):
    """Serializable record for one benchmark example processed by a pipeline."""

    model_config = ConfigDict(extra="forbid")

    run_id: str = Field(min_length=1)
    pipeline: Literal["A", "B", "C", "D"]
    example_id: str = Field(min_length=1)
    dataset_version: str = Field(min_length=1)
    model_adapter: str = Field(min_length=1)
    input_modality: Literal["text", "audio"]
    raw_output: str
    parsed_output: dict[str, Any] | None
    first_pass_parsable: bool
    repair_attempted: bool
    repair_success: bool
    validation_errors: list[str] = Field(default_factory=list)
    structured_failures: list[StructuredToolFailure] = Field(default_factory=list)
    transcript: str | None = None
    wer: float | None = None
    tool_execution_result: ToolResult | None = None
    final_answer: str | None = None
    # Advanced phase fields. Optional so existing artifacts stay valid; they
    # capture which adapter/profile produced the run, the tool manifest in
    # effect, optional speech output, and runtime skips that are distinct from
    # model-output failures.
    adapter_id: str | None = None
    adapter_capabilities: dict[str, Any] | None = None
    inference_profile: str | None = None
    tool_manifest_snapshot: list[ToolManifest] = Field(default_factory=list)
    speech_output: SpeechOutputArtifact | None = None
    runtime_skip_reason: str | None = None


def read_pipeline_jsonl(path: Path) -> list[PipelineRunRecord]:
    """Read pipeline run records from a UTF-8 JSONL artifact."""
    records: list[PipelineRunRecord] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                records.append(PipelineRunRecord.model_validate(json.loads(line)))
    return records


def write_pipeline_jsonl(path: Path, records: Iterable[PipelineRunRecord]) -> int:
    """Write pipeline run records as UTF-8 JSONL and return the count."""
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as file:
        for record in records:
            file.write(json.dumps(record.model_dump(mode="json"), ensure_ascii=False))
            file.write("\n")
            count += 1
    return count
