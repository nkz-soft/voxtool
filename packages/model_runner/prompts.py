from __future__ import annotations

import json
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from packages.tool_schema.providers import ToolRegistry
from packages.tool_schema.units import default_tool_registry

PROMPT_DIR = Path(__file__).resolve().parents[2] / "configs" / "prompts"


class PromptTemplateName(StrEnum):
    PIPELINE_A_TEXT_TOOL = "pipeline_a_text_tool"
    PIPELINE_B_TRANSCRIPT = "pipeline_b_transcript"
    PIPELINE_C_AUDIO_TOOL = "pipeline_c_audio_tool"
    PIPELINE_D_TRANSCRIPT_TOOL = "pipeline_d_transcript_tool"


class PromptTemplate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: PromptTemplateName
    path: Path
    text: str


def load_prompt_template(name: PromptTemplateName) -> PromptTemplate:
    path = PROMPT_DIR / f"{name.value}.md"
    return PromptTemplate(
        name=name,
        path=path,
        text=path.read_text(encoding="utf-8"),
    )


def build_prompt(
    name: PromptTemplateName,
    *,
    registry: ToolRegistry | None = None,
    input_text: str = "",
    transcript: str = "",
) -> str:
    template = load_prompt_template(name)
    active_registry = registry if registry is not None else default_tool_registry()
    tools_json = json.dumps(
        [
            manifest.model_dump(mode="json")
            for manifest in active_registry.build_manifests()
        ],
        indent=2,
        sort_keys=True,
    )
    return template.text.format(
        input_text=input_text,
        transcript=transcript,
        tools_json=tools_json,
    )
