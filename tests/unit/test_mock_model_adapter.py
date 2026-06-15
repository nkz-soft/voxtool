from packages.model_runner.mock import MockModelAdapter


def test_mock_model_adapter_returns_valid_tool_output() -> None:
    adapter = MockModelAdapter()

    output = adapter.generate_text("Convert 2 kilometers to meters.")

    assert output.adapter_name == "MockModelAdapter"
    assert '"needs_tool": true' in output.raw_output
    assert '"from_unit": "kilometer"' in output.raw_output
    assert '"to_unit": "meter"' in output.raw_output


def test_mock_model_adapter_handles_russian_conversion() -> None:
    adapter = MockModelAdapter()

    output = adapter.generate_text("Сконвертируй 2 километра в метры.")

    assert '"needs_tool": true' in output.raw_output
    assert '"from_unit": "kilometer"' in output.raw_output
    assert '"to_unit": "meter"' in output.raw_output
    assert '"value": 2' in output.raw_output


def test_mock_model_adapter_maps_russian_mass_units() -> None:
    adapter = MockModelAdapter()

    output = adapter.generate_text("Переведи 500 граммов в килограммы.")

    assert '"from_unit": "gram"' in output.raw_output
    assert '"to_unit": "kilogram"' in output.raw_output


def test_mock_model_adapter_russian_question_needs_no_tool() -> None:
    adapter = MockModelAdapter()

    output = adapter.generate_text("Какая столица Франции?")

    assert '"needs_tool": false' in output.raw_output
    assert '"tool_call": null' in output.raw_output


def test_mock_model_adapter_returns_no_tool_output() -> None:
    adapter = MockModelAdapter()

    output = adapter.generate_text("Hello there.")

    assert '"needs_tool": false' in output.raw_output
    assert '"tool_call": null' in output.raw_output


def test_mock_model_adapter_can_return_invalid_json() -> None:
    adapter = MockModelAdapter(response_overrides={"bad-json": "this is not json"})

    output = adapter.generate_text("bad-json")

    assert output.raw_output == "this is not json"


def test_mock_model_adapter_can_return_repaired_json() -> None:
    adapter = MockModelAdapter(
        response_overrides={
            "repair": (
                'Here is the JSON: {"needs_tool": false, "tool_call": null, '
                '"final_answer": "No conversion needed."}'
            )
        }
    )

    output = adapter.generate_text("repair")

    assert output.raw_output.startswith("Here is the JSON:")


def test_mock_model_adapter_can_return_invalid_schema_output() -> None:
    adapter = MockModelAdapter(
        response_overrides={
            "invalid-schema": (
                '{"needs_tool": true, "tool_call": null, '
                '"final_answer": "Missing tool call."}'
            )
        }
    )

    output = adapter.generate_text("invalid-schema")

    assert '"needs_tool": true' in output.raw_output
    assert '"tool_call": null' in output.raw_output
