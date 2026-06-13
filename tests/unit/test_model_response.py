from packages.model_runner.adapters import ModelResponse


def test_model_response_retains_raw_output_exactly() -> None:
    raw = 'Here is the JSON: {"needs_tool": false}'

    response = ModelResponse(raw_output=raw)

    assert response.raw_output == raw
    assert response.parsed_output is None
    assert response.metadata == {}
    assert response.error is None


def test_model_response_carries_optional_parsed_envelope_and_metadata() -> None:
    response = ModelResponse(
        raw_output='{"needs_tool": false, "tool_call": null}',
        parsed_output={"needs_tool": False, "tool_call": None},
        metadata={"adapter_id": "qwen", "latency_ms": 12.5},
    )

    assert response.parsed_output == {"needs_tool": False, "tool_call": None}
    assert response.metadata["adapter_id"] == "qwen"


def test_model_response_allows_adapter_error_without_raw_output() -> None:
    response = ModelResponse(error="model runtime unavailable")

    assert response.raw_output == ""
    assert response.parsed_output is None
    assert response.error == "model runtime unavailable"


def test_model_response_round_trips_through_json() -> None:
    response = ModelResponse(raw_output="raw", metadata={"k": "v"})

    restored = ModelResponse.model_validate(response.model_dump(mode="json"))

    assert restored == response
