from typing import Any

from packages.tool_schema import (
    ToolCall,
    ToolExecutor,
    ToolRegistry,
    UnitsConvertProvider,
)
from pydantic import BaseModel, ConfigDict


def test_executor_runs_valid_registered_tool_call() -> None:
    executor = ToolExecutor(ToolRegistry([UnitsConvertProvider()]))

    result = executor.execute(
        ToolCall(
            tool="units.convert",
            arguments={
                "value": 2,
                "from_unit": "kilometer",
                "to_unit": "meter",
            },
        )
    )

    assert result.success is True
    assert result.failure is None
    assert result.result == {
        "result_value": 2000.0,
        "result_unit": "meter",
        "rounded_display": "2000 meter",
    }


def test_executor_returns_structured_failure_for_unknown_tool() -> None:
    executor = ToolExecutor(ToolRegistry([UnitsConvertProvider()]))

    result = executor.execute(ToolCall(tool="weather.lookup", arguments={}))

    assert result.success is False
    assert result.failure is not None
    assert result.failure.failure_type == "unknown_tool"
    assert result.failure.stage == "registry"


def test_executor_returns_structured_failure_for_invalid_arguments() -> None:
    executor = ToolExecutor(ToolRegistry([UnitsConvertProvider()]))

    result = executor.execute(
        ToolCall(
            tool="units.convert",
            arguments={
                "value": "two",
                "from_unit": "kilometer",
                "to_unit": "meter",
            },
        )
    )

    assert result.success is False
    assert result.failure is not None
    assert result.failure.failure_type == "invalid_arguments"
    assert result.failure.stage == "validation"


def test_executor_returns_structured_failure_for_execution_errors() -> None:
    class Args(BaseModel):
        model_config = ConfigDict(extra="forbid")

        value: int

    class FailingProvider:
        name = "test.fail"
        description = "Always fails for testing."
        argument_schema = Args
        deterministic = True

        def json_schema(self) -> dict[str, Any]:
            return self.argument_schema.model_json_schema()

        def execute(self, arguments: BaseModel) -> dict[str, Any]:
            raise RuntimeError("boom")

    executor = ToolExecutor(ToolRegistry([FailingProvider()]))

    result = executor.execute(ToolCall(tool="test.fail", arguments={"value": 1}))

    assert result.success is False
    assert result.failure is not None
    assert result.failure.failure_type == "execution_error"
    assert result.failure.stage == "execution"
