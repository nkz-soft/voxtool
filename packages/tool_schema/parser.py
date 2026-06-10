from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any, cast

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from packages.tool_schema.json_schema import validate_model_output
from packages.tool_schema.models import ModelOutputEnvelope
from packages.tool_schema.providers import (
    StructuredToolFailure,
    ToolCall,
    ToolRegistry,
)
from packages.tool_schema.repair import repair_json_once
from packages.tool_schema.units import default_tool_registry


class ParserResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    raw_output: str
    parsed_json: dict[str, Any] | None = None
    envelope: ModelOutputEnvelope | None = None
    first_pass_parsable: bool
    repair_attempted: bool = False
    repair_success: bool = False
    validation_errors: list[str] = Field(default_factory=list)
    structured_failures: list[StructuredToolFailure] = Field(default_factory=list)

    @property
    def valid(self) -> bool:
        return self.envelope is not None and not self.validation_errors


def parse_model_output(
    raw_output: str,
    *,
    registry: ToolRegistry | None = None,
) -> ParserResult:
    active_registry = registry if registry is not None else default_tool_registry()
    parse_result = _parse_json_with_single_repair(raw_output)

    if parse_result.parsed_json is None:
        return ParserResult(
            raw_output=raw_output,
            first_pass_parsable=parse_result.first_pass_parsable,
            repair_attempted=parse_result.repair_attempted,
            repair_success=parse_result.repair_success,
            validation_errors=[parse_result.error or "Invalid JSON output."],
        )

    validation_errors = _validate_envelope_shape(parse_result.parsed_json)
    if validation_errors:
        return ParserResult(
            raw_output=raw_output,
            parsed_json=parse_result.parsed_json,
            first_pass_parsable=parse_result.first_pass_parsable,
            repair_attempted=parse_result.repair_attempted,
            repair_success=parse_result.repair_success,
            validation_errors=validation_errors,
        )

    structured_failures = _validate_registered_tool_call(
        parse_result.parsed_json,
        active_registry,
    )
    if structured_failures:
        return ParserResult(
            raw_output=raw_output,
            parsed_json=parse_result.parsed_json,
            first_pass_parsable=parse_result.first_pass_parsable,
            repair_attempted=parse_result.repair_attempted,
            repair_success=parse_result.repair_success,
            structured_failures=structured_failures,
        )

    try:
        envelope = ModelOutputEnvelope.model_validate(parse_result.parsed_json)
    except ValidationError as exc:
        return ParserResult(
            raw_output=raw_output,
            parsed_json=parse_result.parsed_json,
            first_pass_parsable=parse_result.first_pass_parsable,
            repair_attempted=parse_result.repair_attempted,
            repair_success=parse_result.repair_success,
            validation_errors=[error["msg"] for error in exc.errors(include_url=False)],
        )

    return ParserResult(
        raw_output=raw_output,
        parsed_json=parse_result.parsed_json,
        envelope=envelope,
        first_pass_parsable=parse_result.first_pass_parsable,
        repair_attempted=parse_result.repair_attempted,
        repair_success=parse_result.repair_success,
    )


class _JsonParseResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    parsed_json: dict[str, Any] | None
    first_pass_parsable: bool
    repair_attempted: bool
    repair_success: bool
    error: str | None = None


def _parse_json_with_single_repair(raw_output: str) -> _JsonParseResult:
    try:
        parsed = _load_json_object(raw_output)
    except ValueError as exc:
        repair_candidate = repair_json_once(raw_output)
        if repair_candidate is None:
            return _JsonParseResult(
                parsed_json=None,
                first_pass_parsable=False,
                repair_attempted=True,
                repair_success=False,
                error=f"Invalid JSON: {exc}",
            )

        try:
            repaired = _load_json_object(repair_candidate)
        except ValueError as repair_exc:
            return _JsonParseResult(
                parsed_json=None,
                first_pass_parsable=False,
                repair_attempted=True,
                repair_success=False,
                error=f"Invalid repaired JSON: {repair_exc}",
            )

        return _JsonParseResult(
            parsed_json=repaired,
            first_pass_parsable=False,
            repair_attempted=True,
            repair_success=True,
        )

    return _JsonParseResult(
        parsed_json=parsed,
        first_pass_parsable=True,
        repair_attempted=False,
        repair_success=False,
    )


def _load_json_object(raw_output: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError as exc:
        raise ValueError(exc.msg) from exc
    if not isinstance(parsed, dict):
        raise ValueError("model output must be a JSON object")
    return cast(dict[str, Any], parsed)


def _validate_envelope_shape(parsed_json: Mapping[str, Any]) -> list[str]:
    if (
        parsed_json.get("needs_tool") is False
        and parsed_json.get("tool_call") is not None
    ):
        return ["tool_call must be null when needs_tool is false"]
    if parsed_json.get("needs_tool") is True and parsed_json.get("tool_call") is None:
        return ["tool_call is required when needs_tool is true"]

    try:
        validate_model_output(parsed_json)
    except ValueError as exc:
        return [str(exc)]
    return []


def _validate_registered_tool_call(
    parsed_json: Mapping[str, Any],
    registry: ToolRegistry,
) -> list[StructuredToolFailure]:
    if parsed_json.get("needs_tool") is not True:
        return []

    tool_call = parsed_json.get("tool_call")
    if not isinstance(tool_call, Mapping):
        return []

    call = ToolCall(
        tool=str(tool_call.get("tool", "")),
        arguments=dict(tool_call.get("arguments", {})),
    )
    validation_result = registry.validate_call(call)
    if isinstance(validation_result, StructuredToolFailure):
        return [validation_result]
    return []
