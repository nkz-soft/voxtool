from packages.tool_schema import ToolRegistry, UnitsConvertProvider, parse_model_output


def test_parser_accepts_consistent_no_tool_envelope() -> None:
    result = parse_model_output(
        '{"needs_tool": false, "tool_call": null, "final_answer": "Answer directly."}',
        registry=ToolRegistry([UnitsConvertProvider()]),
    )

    assert result.envelope is not None
    assert result.validation_errors == []
    assert result.structured_failures == []


def test_parser_rejects_false_alarm_tool_call_when_tool_not_needed() -> None:
    result = parse_model_output(
        """
        {
          "needs_tool": false,
          "tool_call": {
            "tool": "units.convert",
            "arguments": {"value": 1, "from_unit": "meter", "to_unit": "centimeter"}
          },
          "final_answer": "100 centimeters."
        }
        """,
        registry=ToolRegistry([UnitsConvertProvider()]),
    )

    assert result.envelope is None
    assert any("tool_call must be null" in error for error in result.validation_errors)


def test_parser_records_unknown_tool_failure() -> None:
    result = parse_model_output(
        """
        {
          "needs_tool": true,
          "tool_call": {"tool": "weather.lookup", "arguments": {"city": "London"}},
          "final_answer": "I need weather."
        }
        """,
        registry=ToolRegistry([UnitsConvertProvider()]),
    )

    assert result.envelope is None
    assert len(result.structured_failures) == 1
    assert result.structured_failures[0].failure_type == "unknown_tool"
    assert result.structured_failures[0].stage == "registry"


def test_parser_records_invalid_tool_arguments_failure() -> None:
    result = parse_model_output(
        """
        {
          "needs_tool": true,
          "tool_call": {
            "tool": "units.convert",
            "arguments": {"value": "two", "from_unit": "kilometer", "to_unit": "meter"}
          },
          "final_answer": "Invalid arguments."
        }
        """,
        registry=ToolRegistry([UnitsConvertProvider()]),
    )

    assert result.envelope is None
    assert len(result.structured_failures) == 1
    assert result.structured_failures[0].failure_type == "invalid_arguments"
    assert result.structured_failures[0].stage == "validation"
