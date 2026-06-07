import math

import pytest
from packages.tool_schema import ToolInvocation, execute_units_convert
from packages.tool_schema.executor import UnitConversionError


def convert(value: float, from_unit: str, to_unit: str) -> float:
    invocation = ToolInvocation.model_validate(
        {
            "tool": "units.convert",
            "arguments": {
                "value": value,
                "from_unit": from_unit,
                "to_unit": to_unit,
            },
        }
    )
    return execute_units_convert(invocation).result_value


def test_length_conversion() -> None:
    assert convert(2.5, "kilometer", "meter") == 2500
    assert convert(120, "centimeter", "meter") == 1.2
    assert convert(7, "meter", "millimeter") == 7000


def test_mass_conversion() -> None:
    assert convert(1, "kilogram", "gram") == 1000
    assert math.isclose(convert(1, "pound", "ounce"), 16)


def test_temperature_conversion() -> None:
    assert convert(0, "celsius", "fahrenheit") == 32
    assert convert(212, "fahrenheit", "celsius") == 100


def test_same_unit_conversion_is_allowed() -> None:
    result = convert(42, "meter", "meter")

    assert result == 42


def test_incompatible_family_is_rejected() -> None:
    invocation = ToolInvocation.model_validate(
        {
            "tool": "units.convert",
            "arguments": {
                "value": 1,
                "from_unit": "meter",
                "to_unit": "gram",
            },
        }
    )

    with pytest.raises(UnitConversionError, match="Incompatible unit families"):
        execute_units_convert(invocation)


def test_unsupported_unit_is_rejected_before_execution() -> None:
    with pytest.raises(ValueError, match="yard"):
        ToolInvocation.model_validate(
            {
                "tool": "units.convert",
                "arguments": {
                    "value": 1,
                    "from_unit": "yard",
                    "to_unit": "meter",
                },
            }
        )


def test_execution_result_contains_display_value_and_original_arguments() -> None:
    invocation = ToolInvocation.model_validate(
        {
            "tool": "units.convert",
            "arguments": {
                "value": 1,
                "from_unit": "kilometer",
                "to_unit": "meter",
            },
        }
    )

    result = execute_units_convert(invocation)

    assert result.tool == "units.convert"
    assert result.result_unit == "meter"
    assert result.rounded_display == "1000 meter"
    assert result.arguments == invocation.arguments
    assert result.execution_error is None
