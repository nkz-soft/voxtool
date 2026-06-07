from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Unit(StrEnum):
    METER = "meter"
    KILOMETER = "kilometer"
    CENTIMETER = "centimeter"
    MILLIMETER = "millimeter"
    GRAM = "gram"
    KILOGRAM = "kilogram"
    POUND = "pound"
    OUNCE = "ounce"
    CELSIUS = "celsius"
    FAHRENHEIT = "fahrenheit"


class UnitFamily(StrEnum):
    LENGTH = "length"
    MASS = "mass"
    TEMPERATURE = "temperature"


class ToolArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: float
    from_unit: Unit
    to_unit: Unit


class ToolInvocation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool: Literal["units.convert"]
    arguments: ToolArguments


class ModelOutputEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    needs_tool: bool
    tool_call: ToolInvocation | None
    final_answer: str = Field(min_length=1)
    transcript: str | None = None

    @model_validator(mode="after")
    def validate_tool_consistency(self) -> "ModelOutputEnvelope":
        if self.needs_tool and self.tool_call is None:
            raise ValueError("tool_call is required when needs_tool is true")
        if not self.needs_tool and self.tool_call is not None:
            raise ValueError("tool_call must be null when needs_tool is false")
        return self


class ToolValidationError(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str
    path: list[str | int] = Field(default_factory=list)
    validator: str | None = None


class ToolExecutionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool: Literal["units.convert"]
    arguments: ToolArguments
    result_value: float
    result_unit: Unit
    rounded_display: str
    execution_error: str | None = None
