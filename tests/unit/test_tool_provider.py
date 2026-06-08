from typing import Any

from packages.tool_schema import ToolArguments, ToolProvider, UnitsConvertProvider


def test_units_convert_provider_exposes_common_interface() -> None:
    provider: ToolProvider = UnitsConvertProvider()

    assert provider.name == "units.convert"
    assert "Convert" in provider.description
    assert provider.argument_schema is ToolArguments
    assert provider.deterministic is True


def test_units_convert_provider_exports_json_schema() -> None:
    provider = UnitsConvertProvider()
    schema: dict[str, Any] = provider.json_schema()

    assert schema["type"] == "object"
    assert set(schema["required"]) == {"value", "from_unit", "to_unit"}
    assert "properties" in schema
