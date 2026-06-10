from packages.tool_schema import ToolRegistry, UnitsConvertProvider, parse_model_output


def test_parser_accepts_valid_first_pass_envelope() -> None:
    result = parse_model_output(
        """
        {
          "needs_tool": true,
          "tool_call": {
            "tool": "units.convert",
            "arguments": {
              "value": 2,
              "from_unit": "kilometer",
              "to_unit": "meter"
            }
          },
          "final_answer": "2 kilometers is 2000 meters."
        }
        """,
        registry=ToolRegistry([UnitsConvertProvider()]),
    )

    assert result.first_pass_parsable is True
    assert result.repair_attempted is False
    assert result.repair_success is False
    assert result.envelope is not None
    assert result.envelope.needs_tool is True
    assert result.validation_errors == []
    assert result.structured_failures == []


def test_parser_records_invalid_json_without_repair_success() -> None:
    result = parse_model_output(
        "this is not json",
        registry=ToolRegistry([UnitsConvertProvider()]),
    )

    assert result.first_pass_parsable is False
    assert result.repair_attempted is True
    assert result.repair_success is False
    assert result.envelope is None
    assert result.validation_errors


def test_parser_repairs_single_wrapped_json_object() -> None:
    result = parse_model_output(
        """Here is the JSON:
        {"needs_tool": false, "tool_call": null, "final_answer": "No tool needed."}
        Done.""",
        registry=ToolRegistry([UnitsConvertProvider()]),
    )

    assert result.first_pass_parsable is False
    assert result.repair_attempted is True
    assert result.repair_success is True
    assert result.envelope is not None
    assert result.envelope.needs_tool is False


def test_parser_records_failed_repair() -> None:
    result = parse_model_output(
        '{"needs_tool": true, "tool_call": ',
        registry=ToolRegistry([UnitsConvertProvider()]),
    )

    assert result.first_pass_parsable is False
    assert result.repair_attempted is True
    assert result.repair_success is False
    assert result.parsed_json is None
    assert result.validation_errors
