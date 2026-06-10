"""Tool schema validation and execution package."""

from packages.tool_schema.executor import UnitConversionError, execute_units_convert
from packages.tool_schema.json_schema import (
    build_registered_tool_prompt_schema,
    load_model_output_schema,
    validate_model_output,
)
from packages.tool_schema.models import (
    ModelOutputEnvelope,
    ToolArguments,
    ToolExecutionResult,
    ToolInvocation,
    ToolValidationError,
    Unit,
    UnitFamily,
)
from packages.tool_schema.parser import ParserResult, parse_model_output
from packages.tool_schema.providers import (
    StructuredToolFailure,
    ToolCall,
    ToolExecutor,
    ToolManifest,
    ToolProvider,
    ToolRegistry,
    ToolResult,
)
from packages.tool_schema.repair import repair_json_once
from packages.tool_schema.units import UnitsConvertProvider, default_tool_registry

__all__ = [
    "ModelOutputEnvelope",
    "ParserResult",
    "StructuredToolFailure",
    "ToolArguments",
    "ToolCall",
    "ToolExecutor",
    "ToolExecutionResult",
    "ToolInvocation",
    "ToolManifest",
    "ToolProvider",
    "ToolRegistry",
    "ToolResult",
    "ToolValidationError",
    "Unit",
    "UnitConversionError",
    "UnitFamily",
    "UnitsConvertProvider",
    "build_registered_tool_prompt_schema",
    "default_tool_registry",
    "execute_units_convert",
    "load_model_output_schema",
    "parse_model_output",
    "repair_json_once",
    "validate_model_output",
]
