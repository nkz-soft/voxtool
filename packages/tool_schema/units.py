from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel

from packages.tool_schema.executor import execute_units_convert
from packages.tool_schema.models import ToolArguments, ToolInvocation
from packages.tool_schema.providers import ToolRegistry


class UnitsConvertProvider:
    name: Literal["units.convert"] = "units.convert"
    description = (
        "Convert a numeric value between supported length, mass, or temperature units."
    )
    argument_schema: type[BaseModel] = ToolArguments
    deterministic = True

    def json_schema(self) -> dict[str, Any]:
        return self.argument_schema.model_json_schema()

    def execute(self, arguments: BaseModel) -> dict[str, Any]:
        typed_arguments = ToolArguments.model_validate(arguments)
        result = execute_units_convert(
            ToolInvocation(tool="units.convert", arguments=typed_arguments)
        )
        return {
            "result_value": result.result_value,
            "result_unit": result.result_unit.value,
            "rounded_display": result.rounded_display,
        }


def default_tool_registry() -> ToolRegistry:
    return ToolRegistry([UnitsConvertProvider()])
