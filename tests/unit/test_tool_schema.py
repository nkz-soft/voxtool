from packages.tool_schema import ModelOutputEnvelope, ToolInvocation, Unit
from pydantic import ValidationError


def test_valid_tool_envelope_parses_to_typed_model() -> None:
    envelope = ModelOutputEnvelope.model_validate(
        {
            "needs_tool": True,
            "tool_call": {
                "tool": "units.convert",
                "arguments": {
                    "value": 2.5,
                    "from_unit": "kilometer",
                    "to_unit": "meter",
                },
            },
            "final_answer": "2.5 kilometers is 2500 meters.",
        }
    )

    assert envelope.needs_tool is True
    assert isinstance(envelope.tool_call, ToolInvocation)
    assert envelope.tool_call.arguments.from_unit is Unit.KILOMETER
    assert envelope.tool_call.arguments.to_unit is Unit.METER


def test_valid_no_tool_envelope_requires_null_tool_call() -> None:
    envelope = ModelOutputEnvelope.model_validate(
        {
            "needs_tool": False,
            "tool_call": None,
            "final_answer": "No conversion is needed.",
        }
    )

    assert envelope.needs_tool is False
    assert envelope.tool_call is None


def test_rejects_tool_call_when_needs_tool_is_false() -> None:
    with pytest_raises_validation("tool_call must be null"):
        ModelOutputEnvelope.model_validate(
            {
                "needs_tool": False,
                "tool_call": {
                    "tool": "units.convert",
                    "arguments": {
                        "value": 1,
                        "from_unit": "meter",
                        "to_unit": "centimeter",
                    },
                },
                "final_answer": "100 centimeters.",
            }
        )


def test_rejects_missing_tool_call_when_needs_tool_is_true() -> None:
    with pytest_raises_validation("tool_call is required"):
        ModelOutputEnvelope.model_validate(
            {
                "needs_tool": True,
                "tool_call": None,
                "final_answer": "100 centimeters.",
            }
        )


def test_rejects_unknown_unit_and_extra_fields() -> None:
    with pytest_raises_validation("Input should be"):
        ModelOutputEnvelope.model_validate(
            {
                "needs_tool": True,
                "tool_call": {
                    "tool": "units.convert",
                    "arguments": {
                        "value": 1,
                        "from_unit": "meter",
                        "to_unit": "yard",
                        "precision": 2,
                    },
                },
                "final_answer": "Invalid unit.",
            }
        )


def test_transcript_is_optional() -> None:
    envelope = ModelOutputEnvelope.model_validate(
        {
            "needs_tool": False,
            "tool_call": None,
            "final_answer": "The transcript does not need a tool.",
            "transcript": "convert nothing",
        }
    )

    assert envelope.transcript == "convert nothing"


class pytest_raises_validation:
    def __init__(self, expected_message: str) -> None:
        self.expected_message = expected_message

    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> bool:
        assert exc_type is ValidationError
        assert self.expected_message in str(exc)
        return True
