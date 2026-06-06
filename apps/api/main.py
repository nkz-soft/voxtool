from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="VoxTool Demo API")


class ToolRequest(BaseModel):
    """Minimal request shape for future validated tool execution."""

    tool_name: str
    arguments: dict[str, Any]


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
