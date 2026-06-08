import pytest
from packages.tool_schema import (
    ToolCall,
    ToolManifest,
    ToolRegistry,
    ToolResult,
    UnitsConvertProvider,
)
from pydantic import ValidationError


def test_tool_call_requires_tool_name() -> None:
    with pytest.raises(ValidationError):
        ToolCall(tool="", arguments={})


def test_tool_result_represents_success() -> None:
    result = ToolResult(
        tool="units.convert",
        arguments={"value": 1, "from_unit": "kilometer", "to_unit": "meter"},
        result={"result_value": 1000, "result_unit": "meter"},
    )

    assert result.success is True
    assert result.failure is None


def test_registry_builds_tool_manifests() -> None:
    manifests = ToolRegistry([UnitsConvertProvider()]).build_manifests()

    assert manifests == [
        ToolManifest(
            name="units.convert",
            description=UnitsConvertProvider().description,
            arguments_json_schema=UnitsConvertProvider().json_schema(),
        )
    ]
