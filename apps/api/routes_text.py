from __future__ import annotations

from fastapi import APIRouter, Request
from packages.dataset_builder.models import Language
from packages.model_runner.prompts import PromptTemplateName, build_prompt
from pydantic import BaseModel, ConfigDict, Field

from apps.api.demo import DemoResponse, run_demo_prompt

router = APIRouter()


class TextDemoRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)
    language: Language = "en"
    execute_tool: bool = True


@router.post("/demo/text")
def demo_text(request: TextDemoRequest, http_request: Request) -> DemoResponse:
    """Run the Pipeline A text tool-calling flow for one demo input."""
    state = http_request.app.state
    prompt = build_prompt(
        PromptTemplateName.PIPELINE_A_TEXT_TOOL,
        registry=state.registry,
        input_text=request.text,
    )
    return run_demo_prompt(
        prompt,
        text_adapter=state.text_adapter,
        registry=state.registry,
        executor=state.executor,
        execute_tool=request.execute_tool,
    )
