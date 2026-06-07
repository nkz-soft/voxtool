import json
from pathlib import Path

import pytest
from packages.tool_schema.json_schema import (
    load_model_output_schema,
    validate_model_output,
)

SPEC_SCHEMA_PATH = Path(
    "specs/002-voice-benchmark-demo/contracts/model-output.schema.json"
)
CONFIG_SCHEMA_PATH = Path("configs/tools/model-output.schema.json")


def test_runtime_schema_copy_matches_spec_contract() -> None:
    spec_schema = json.loads(SPEC_SCHEMA_PATH.read_text(encoding="utf-8"))
    config_schema = json.loads(CONFIG_SCHEMA_PATH.read_text(encoding="utf-8"))

    assert config_schema == spec_schema


def test_json_schema_accepts_valid_tool_envelope() -> None:
    validate_model_output(
        {
            "needs_tool": True,
            "tool_call": {
                "tool": "units.convert",
                "arguments": {
                    "value": 2,
                    "from_unit": "kilogram",
                    "to_unit": "gram",
                },
            },
            "final_answer": "2 kilograms is 2000 grams.",
        },
        schema=load_model_output_schema(SPEC_SCHEMA_PATH),
    )


@pytest.mark.parametrize(
    "payload",
    [
        {
            "needs_tool": False,
            "tool_call": {
                "tool": "units.convert",
                "arguments": {
                    "value": 2,
                    "from_unit": "kilogram",
                    "to_unit": "gram",
                },
            },
            "final_answer": "2 kilograms is 2000 grams.",
        },
        {
            "needs_tool": True,
            "tool_call": None,
            "final_answer": "2 kilograms is 2000 grams.",
        },
        {
            "needs_tool": True,
            "tool_call": {
                "tool": "weather.lookup",
                "arguments": {
                    "value": 2,
                    "from_unit": "kilogram",
                    "to_unit": "gram",
                },
            },
            "final_answer": "Unsupported.",
        },
    ],
)
def test_json_schema_rejects_invalid_envelopes(payload: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        validate_model_output(
            payload,
            schema=load_model_output_schema(SPEC_SCHEMA_PATH),
        )
