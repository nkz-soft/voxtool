from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Literal, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

FailureType = Literal[
    "unknown_tool",
    "duplicate_tool_provider",
    "invalid_arguments",
    "execution_error",
]
FailureStage = Literal["registry", "validation", "execution"]


class ToolCall(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool: str = Field(min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)


class StructuredToolFailure(BaseModel):
    model_config = ConfigDict(extra="forbid")

    failure_type: FailureType
    tool: str | None = None
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    stage: FailureStage


class ToolResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    result: dict[str, Any] | None = None
    failure: StructuredToolFailure | None = None
    success: bool = True

    @model_validator(mode="after")
    def derive_success(self) -> ToolResult:
        self.success = self.failure is None
        return self


class ToolManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    arguments_json_schema: dict[str, Any]


@runtime_checkable
class ToolProvider(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def description(self) -> str: ...

    @property
    def argument_schema(self) -> type[BaseModel]: ...

    @property
    def deterministic(self) -> bool: ...

    def json_schema(self) -> dict[str, Any]: ...

    def execute(self, arguments: BaseModel) -> dict[str, Any]: ...


class ToolRegistry:
    def __init__(self, providers: Iterable[ToolProvider] = ()) -> None:
        self._providers: dict[str, ToolProvider] = {}
        for provider in providers:
            self.register(provider)

    def register(self, provider: ToolProvider) -> None:
        if provider.name in self._providers:
            raise ValueError(f"Duplicate tool provider: {provider.name}")
        self._providers[provider.name] = provider

    def get(self, name: str) -> ToolProvider | None:
        return self._providers.get(name)

    def resolve(self, name: str) -> ToolProvider | StructuredToolFailure:
        provider = self.get(name)
        if provider is not None:
            return provider
        return StructuredToolFailure(
            failure_type="unknown_tool",
            tool=name,
            message="Tool is not registered.",
            details={"available_tools": sorted(self._providers)},
            stage="registry",
        )

    def build_manifests(self) -> list[ToolManifest]:
        return [
            ToolManifest(
                name=provider.name,
                description=provider.description,
                arguments_json_schema=provider.json_schema(),
            )
            for provider in self._providers.values()
        ]

    def prompt_schema(self) -> dict[str, Any]:
        return {
            "tools": [
                manifest.model_dump(mode="json") for manifest in self.build_manifests()
            ]
        }

    def validate_call(self, call: ToolCall) -> BaseModel | StructuredToolFailure:
        resolved = self.resolve(call.tool)
        if isinstance(resolved, StructuredToolFailure):
            return resolved
        try:
            return resolved.argument_schema.model_validate(call.arguments)
        except ValidationError as exc:
            return StructuredToolFailure(
                failure_type="invalid_arguments",
                tool=call.tool,
                message="Tool arguments did not match provider schema.",
                details={"errors": exc.errors(include_url=False)},
                stage="validation",
            )


class ToolExecutor:
    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

    def execute(self, call: ToolCall) -> ToolResult:
        resolved = self.registry.resolve(call.tool)
        if isinstance(resolved, StructuredToolFailure):
            return ToolResult(
                tool=call.tool,
                arguments=call.arguments,
                failure=resolved,
            )

        validated = self.registry.validate_call(call)
        if isinstance(validated, StructuredToolFailure):
            return ToolResult(
                tool=call.tool,
                arguments=call.arguments,
                failure=validated,
            )

        try:
            provider_result = resolved.execute(validated)
        except Exception as exc:
            failure = StructuredToolFailure(
                failure_type="execution_error",
                tool=call.tool,
                message=str(exc),
                details={"exception_type": type(exc).__name__},
                stage="execution",
            )
            return ToolResult(
                tool=call.tool,
                arguments=call.arguments,
                failure=failure,
            )

        return ToolResult(
            tool=call.tool,
            arguments=call.arguments,
            result=provider_result,
        )
