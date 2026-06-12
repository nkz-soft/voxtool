from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from packages.model_runner.asr import ASRAdapter, MockASRAdapter
from packages.model_runner.base import TextModelAdapter
from packages.model_runner.mock import MockModelAdapter
from packages.tool_schema.providers import ToolExecutor, ToolRegistry
from packages.tool_schema.units import default_tool_registry
from pydantic import BaseModel

from apps.api.demo import ToolFailureError
from apps.api.routes_audio import router as audio_router
from apps.api.routes_text import router as text_router


class ToolRequest(BaseModel):
    """Minimal request shape for future validated tool execution."""

    tool_name: str
    arguments: dict[str, Any]


def create_app(
    *,
    text_adapter: TextModelAdapter | None = None,
    asr_adapter: ASRAdapter | None = None,
    registry: ToolRegistry | None = None,
    executor: ToolExecutor | None = None,
) -> FastAPI:
    """Build the optional local demo API with injectable adapter dependencies."""
    app = FastAPI(title="VoxTool Demo API")

    active_registry = registry if registry is not None else default_tool_registry()
    app.state.text_adapter = text_adapter or MockModelAdapter()
    app.state.asr_adapter = asr_adapter or MockASRAdapter()
    app.state.registry = active_registry
    app.state.executor = executor or ToolExecutor(active_registry)

    app.include_router(text_router)
    app.include_router(audio_router)

    @app.exception_handler(ToolFailureError)
    def tool_failure_handler(request: Request, exc: ToolFailureError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "tool_failure",
                    "message": "Tool call could not be completed.",
                    "details": {
                        "structured_failures": [
                            failure.model_dump(mode="json") for failure in exc.failures
                        ]
                    },
                }
            },
        )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/tools/validate")
    def validate_tool_request(request: ToolRequest) -> dict[str, Any]:
        return {
            "valid": request.tool_name == "units.convert",
            "tool_name": request.tool_name,
            "arguments": request.arguments,
        }

    return app


app = create_app()
