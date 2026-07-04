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


def test_parser_repairs_echoed_prompt_by_selecting_response_envelope() -> None:
    result = parse_model_output(
        """
        Available tools:
        ```json
        [
          {
            "arguments_json_schema": {"type": "object"},
            "description": "Convert units.",
            "name": "units.convert"
          }
        ]
        ```

        Request:
        Convert 2 kilometers to meters.
        ```json
        {
          "needs_tool": true,
          "tool_call": {
            "name": "units.convert",
            "arguments": {
              "from_unit": "kilometer",
              "to_unit": "meter",
              "value": 2
            }
          },
          "final_answer": null
        }
        ```
        """,
        registry=ToolRegistry([UnitsConvertProvider()]),
    )

    assert result.first_pass_parsable is False
    assert result.repair_attempted is True
    assert result.repair_success is True
    assert result.envelope is not None
    assert result.envelope.tool_call is not None
    assert result.envelope.tool_call.tool == "units.convert"


def test_parser_accepts_tool_call_name_alias_as_canonical_tool() -> None:
    result = parse_model_output(
        """
        {
          "needs_tool": true,
          "tool_call": {
            "name": "units.convert",
            "arguments": {
              "value": 5,
              "from_unit": "kilometer",
              "to_unit": "meter"
            }
          },
          "final_answer": "5000 meters."
        }
        """,
        registry=ToolRegistry([UnitsConvertProvider()]),
    )

    assert result.first_pass_parsable is True
    assert result.envelope is not None
    assert result.parsed_json is not None
    assert result.parsed_json["tool_call"]["tool"] == "units.convert"


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
