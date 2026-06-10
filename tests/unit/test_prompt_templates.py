import json

from packages.model_runner.prompts import (
    PromptTemplateName,
    build_prompt,
    load_prompt_template,
)
from packages.tool_schema import ToolRegistry, UnitsConvertProvider


def test_all_pipeline_prompt_templates_are_available() -> None:
    for template_name in PromptTemplateName:
        template = load_prompt_template(template_name)
        assert template.name == template_name
        assert template.text.strip()


def test_text_tool_prompt_injects_registered_tool_manifest() -> None:
    registry = ToolRegistry([UnitsConvertProvider()])

    prompt = build_prompt(
        PromptTemplateName.PIPELINE_A_TEXT_TOOL,
        registry=registry,
        input_text="Convert 2 kilometers to meters.",
    )

    manifest_json = json.dumps(
        [manifest.model_dump(mode="json") for manifest in registry.build_manifests()],
        indent=2,
        sort_keys=True,
    )
    assert manifest_json in prompt
    assert "units.convert" in prompt
    assert "Convert 2 kilometers to meters." in prompt


def test_transcript_tool_prompt_injects_transcript_and_tool_manifest() -> None:
    prompt = build_prompt(
        PromptTemplateName.PIPELINE_D_TRANSCRIPT_TOOL,
        registry=ToolRegistry([UnitsConvertProvider()]),
        transcript="Convert 3 pounds to ounces.",
    )

    assert "Convert 3 pounds to ounces." in prompt
    assert "units.convert" in prompt
