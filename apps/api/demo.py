from __future__ import annotations

from typing import Any

from packages.model_runner.base import TextModelAdapter
from packages.tool_schema.parser import parse_model_output
from packages.tool_schema.providers import (
    StructuredToolFailure,
    ToolCall,
    ToolExecutor,
    ToolRegistry,
)
from pydantic import BaseModel, ConfigDict


class ToolFailureError(Exception):
    """Raised when a requested tool execution cannot be completed."""

    def __init__(self, failures: list[StructuredToolFailure]) -> None:
        super().__init__("Tool call could not be completed.")
        self.failures = failures


class DemoResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    raw_output: str
    parsed_output: dict[str, Any] | None
    validation_error: str | None
    structured_failures: list[StructuredToolFailure]
    tool_execution_result: dict[str, Any] | None
    final_answer: str | None


class AudioDemoResponse(DemoResponse):
    transcript: str


def run_demo_prompt(
    prompt: str,
    *,
    text_adapter: TextModelAdapter,
    registry: ToolRegistry,
    executor: ToolExecutor,
    execute_tool: bool,
) -> DemoResponse:
    """Generate, parse, and optionally execute one demo prompt.

    Raises ToolFailureError when execution was requested but the tool call
    failed at any stage (registry, validation, or execution).
    """
    model_output = text_adapter.generate_text(prompt)
    parsed = parse_model_output(model_output.raw_output, registry=registry)
    structured_failures = list(parsed.structured_failures)
    tool_execution_result: dict[str, Any] | None = None

    if (
        execute_tool
        and parsed.envelope is not None
        and parsed.envelope.tool_call is not None
    ):
        tool_result = executor.execute(
            ToolCall(
                tool=parsed.envelope.tool_call.tool,
                arguments=parsed.envelope.tool_call.arguments.model_dump(mode="json"),
            )
        )
        if tool_result.failure is not None:
            structured_failures.append(tool_result.failure)
        elif tool_result.result is not None:
            tool_execution_result = {"tool": tool_result.tool, **tool_result.result}

    if execute_tool and structured_failures:
        raise ToolFailureError(structured_failures)

    final_answer = parsed.envelope.final_answer if parsed.envelope is not None else None
    validation_error = parsed.validation_errors[0] if parsed.validation_errors else None
    return DemoResponse(
        raw_output=parsed.raw_output,
        parsed_output=parsed.parsed_json,
        validation_error=validation_error,
        structured_failures=structured_failures,
        tool_execution_result=tool_execution_result,
        final_answer=final_answer,
    )
