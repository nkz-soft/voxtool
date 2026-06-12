from __future__ import annotations

import json

from apps.api.main import create_app
from fastapi.testclient import TestClient
from packages.model_runner.mock import MockModelAdapter


def _client(text_adapter: MockModelAdapter | None = None) -> TestClient:
    app = create_app(text_adapter=text_adapter or MockModelAdapter())
    return TestClient(app)


def test_text_demo_executes_tool_for_conversion() -> None:
    client = _client()

    response = client.post(
        "/demo/text",
        json={
            "text": "Convert 2 kilometers to meters",
            "language": "en",
            "execute_tool": True,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["raw_output"] != ""
    assert body["parsed_output"]["needs_tool"] is True
    assert body["parsed_output"]["tool_call"]["tool"] == "units.convert"
    assert body["validation_error"] is None
    assert body["structured_failures"] == []
    assert body["tool_execution_result"]["tool"] == "units.convert"
    assert body["tool_execution_result"]["result_value"] == 2000
    assert body["tool_execution_result"]["result_unit"] == "meter"
    assert body["final_answer"] == "2 kilometers is 2000 meters."


def test_text_demo_skips_tool_execution_when_disabled() -> None:
    client = _client()

    response = client.post(
        "/demo/text",
        json={
            "text": "Convert 2 kilometers to meters",
            "language": "en",
            "execute_tool": False,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["parsed_output"]["needs_tool"] is True
    assert body["tool_execution_result"] is None
    assert body["final_answer"] == "2 kilometers is 2000 meters."


def test_text_demo_returns_no_tool_result_when_not_needed() -> None:
    client = _client()

    response = client.post(
        "/demo/text",
        json={"text": "Hello there", "language": "en", "execute_tool": True},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["parsed_output"]["needs_tool"] is False
    assert body["tool_execution_result"] is None
    assert body["final_answer"] is not None


def test_text_demo_reports_validation_error_for_invalid_output() -> None:
    adapter = MockModelAdapter(response_overrides={"Garbled": "not json at all"})
    client = _client(adapter)

    response = client.post(
        "/demo/text",
        json={"text": "Garbled request", "language": "en", "execute_tool": True},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["validation_error"] is not None
    assert body["tool_execution_result"] is None
    assert body["final_answer"] is None


def test_text_demo_returns_error_envelope_for_unknown_tool() -> None:
    unknown_tool_output = json.dumps(
        {
            "needs_tool": True,
            "tool_call": {"tool": "weather.lookup", "arguments": {}},
            "final_answer": "Looked up the weather.",
        }
    )
    adapter = MockModelAdapter(response_overrides={"weather": unknown_tool_output})
    client = _client(adapter)

    response = client.post(
        "/demo/text",
        json={
            "text": "What is the weather today?",
            "language": "en",
            "execute_tool": True,
        },
    )

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "tool_failure"
    failures = body["error"]["details"]["structured_failures"]
    assert failures[0]["failure_type"] == "unknown_tool"
    assert failures[0]["tool"] == "weather.lookup"
    assert failures[0]["stage"] == "registry"


def test_text_demo_rejects_empty_text() -> None:
    client = _client()

    response = client.post(
        "/demo/text",
        json={"text": "", "language": "en", "execute_tool": True},
    )

    assert response.status_code == 422
