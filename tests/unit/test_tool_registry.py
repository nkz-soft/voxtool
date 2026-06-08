import pytest
from packages.tool_schema import (
    StructuredToolFailure,
    ToolRegistry,
    UnitsConvertProvider,
)


def test_registry_resolves_registered_provider() -> None:
    provider = UnitsConvertProvider()
    registry = ToolRegistry([provider])

    assert registry.get("units.convert") is provider


def test_registry_rejects_duplicate_provider_names() -> None:
    with pytest.raises(ValueError, match="Duplicate tool provider"):
        ToolRegistry([UnitsConvertProvider(), UnitsConvertProvider()])


def test_registry_returns_structured_failure_for_unknown_tool() -> None:
    registry = ToolRegistry([UnitsConvertProvider()])

    failure = registry.resolve("weather.lookup")

    assert isinstance(failure, StructuredToolFailure)
    assert failure.failure_type == "unknown_tool"
    assert failure.tool == "weather.lookup"
    assert failure.stage == "registry"


def test_registry_exports_prompt_schema_from_registered_providers() -> None:
    registry = ToolRegistry([UnitsConvertProvider()])

    prompt_schema = registry.prompt_schema()

    assert prompt_schema["tools"][0]["name"] == "units.convert"
    assert "description" in prompt_schema["tools"][0]
    assert "arguments_json_schema" in prompt_schema["tools"][0]
