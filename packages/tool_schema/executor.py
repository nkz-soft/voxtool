from decimal import Decimal

from packages.tool_schema.models import (
    ToolExecutionResult,
    ToolInvocation,
    Unit,
    UnitFamily,
)


class UnitConversionError(ValueError):
    pass


UNIT_FAMILIES: dict[Unit, UnitFamily] = {
    Unit.METER: UnitFamily.LENGTH,
    Unit.KILOMETER: UnitFamily.LENGTH,
    Unit.CENTIMETER: UnitFamily.LENGTH,
    Unit.MILLIMETER: UnitFamily.LENGTH,
    Unit.GRAM: UnitFamily.MASS,
    Unit.KILOGRAM: UnitFamily.MASS,
    Unit.POUND: UnitFamily.MASS,
    Unit.OUNCE: UnitFamily.MASS,
    Unit.CELSIUS: UnitFamily.TEMPERATURE,
    Unit.FAHRENHEIT: UnitFamily.TEMPERATURE,
}

LENGTH_TO_METER: dict[Unit, Decimal] = {
    Unit.METER: Decimal("1"),
    Unit.KILOMETER: Decimal("1000"),
    Unit.CENTIMETER: Decimal("0.01"),
    Unit.MILLIMETER: Decimal("0.001"),
}

MASS_TO_GRAM: dict[Unit, Decimal] = {
    Unit.GRAM: Decimal("1"),
    Unit.KILOGRAM: Decimal("1000"),
    Unit.POUND: Decimal("453.59237"),
    Unit.OUNCE: Decimal("28.349523125"),
}


def execute_units_convert(invocation: ToolInvocation) -> ToolExecutionResult:
    arguments = invocation.arguments
    from_family = UNIT_FAMILIES[arguments.from_unit]
    to_family = UNIT_FAMILIES[arguments.to_unit]
    if from_family != to_family:
        raise UnitConversionError(
            "Incompatible unit families: "
            f"{arguments.from_unit.value} cannot convert to {arguments.to_unit.value}"
        )

    result_value = _convert(
        arguments.value,
        arguments.from_unit,
        arguments.to_unit,
        from_family,
    )
    return ToolExecutionResult(
        tool=invocation.tool,
        arguments=arguments,
        result_value=result_value,
        result_unit=arguments.to_unit,
        rounded_display=f"{_format_number(result_value)} {arguments.to_unit.value}",
        execution_error=None,
    )


def _convert(value: float, from_unit: Unit, to_unit: Unit, family: UnitFamily) -> float:
    if from_unit == to_unit:
        return value

    if family == UnitFamily.LENGTH:
        meters = Decimal(str(value)) * LENGTH_TO_METER[from_unit]
        return float(meters / LENGTH_TO_METER[to_unit])

    if family == UnitFamily.MASS:
        grams = Decimal(str(value)) * MASS_TO_GRAM[from_unit]
        return float(grams / MASS_TO_GRAM[to_unit])

    if family == UnitFamily.TEMPERATURE:
        return _convert_temperature(value, from_unit, to_unit)

    raise UnitConversionError(f"Unsupported unit family: {family.value}")


def _convert_temperature(value: float, from_unit: Unit, to_unit: Unit) -> float:
    if from_unit == Unit.CELSIUS and to_unit == Unit.FAHRENHEIT:
        return (value * 9 / 5) + 32
    if from_unit == Unit.FAHRENHEIT and to_unit == Unit.CELSIUS:
        return (value - 32) * 5 / 9
    raise UnitConversionError(
        f"Unsupported temperature conversion: {from_unit.value} to {to_unit.value}"
    )


def _format_number(value: float) -> str:
    return f"{value:.6g}"
