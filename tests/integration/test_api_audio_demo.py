from __future__ import annotations

import json

from apps.api.main import create_app
from fastapi.testclient import TestClient
from packages.model_runner.asr import MockASRAdapter
from packages.model_runner.mock import MockModelAdapter

CONVERSION_TRANSCRIPT = "Convert 2 kilometers to meters"


def _client(
    text_adapter: MockModelAdapter | None = None,
    asr_adapter: MockASRAdapter | None = None,
) -> TestClient:
    app = create_app(
        text_adapter=text_adapter or MockModelAdapter(),
        asr_adapter=asr_adapter
        or MockASRAdapter(transcript_overrides={"example": CONVERSION_TRANSCRIPT}),
    )
    return TestClient(app)


def test_audio_demo_pipeline_c_executes_tool_for_conversion() -> None:
    client = _client()

    response = client.post(
        "/demo/audio",
        json={
            "audio_path": "data/fixtures/example.wav",
            "language": "en",
            "pipeline": "C",
            "execute_tool": True,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["transcript"] == CONVERSION_TRANSCRIPT
    assert body["raw_output"] != ""
    assert body["parsed_output"]["needs_tool"] is True
    assert body["parsed_output"]["tool_call"]["tool"] == "units.convert"
    assert body["validation_error"] is None
    assert body["structured_failures"] == []
    assert body["tool_execution_result"]["tool"] == "units.convert"
    assert body["tool_execution_result"]["result_value"] == 2000
    assert body["tool_execution_result"]["result_unit"] == "meter"
    assert body["final_answer"] == "2 kilometers is 2000 meters."


def test_audio_demo_pipeline_d_executes_tool_for_conversion() -> None:
    client = _client()

    response = client.post(
        "/demo/audio",
        json={
            "audio_path": "data/fixtures/example.wav",
            "language": "en",
            "pipeline": "D",
            "execute_tool": True,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["transcript"] == CONVERSION_TRANSCRIPT
    assert body["tool_execution_result"]["result_value"] == 2000
    assert body["final_answer"] == "2 kilometers is 2000 meters."


def test_audio_demo_skips_tool_execution_when_disabled() -> None:
    client = _client()

    response = client.post(
        "/demo/audio",
        json={
            "audio_path": "data/fixtures/example.wav",
            "language": "en",
            "pipeline": "C",
            "execute_tool": False,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["parsed_output"]["needs_tool"] is True
    assert body["tool_execution_result"] is None
    assert body["final_answer"] == "2 kilometers is 2000 meters."


def test_audio_demo_returns_error_envelope_for_unknown_tool() -> None:
    unknown_tool_output = json.dumps(
        {
            "needs_tool": True,
            "tool_call": {"tool": "weather.lookup", "arguments": {}},
            "final_answer": "Looked up the weather.",
        }
    )
    text_adapter = MockModelAdapter(response_overrides={"weather": unknown_tool_output})
    asr_adapter = MockASRAdapter(
        transcript_overrides={"example": "What is the weather today?"}
    )
    client = _client(text_adapter, asr_adapter)

    response = client.post(
        "/demo/audio",
        json={
            "audio_path": "data/fixtures/example.wav",
            "language": "en",
            "pipeline": "C",
            "execute_tool": True,
        },
    )

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "tool_failure"
    failures = body["error"]["details"]["structured_failures"]
    assert failures[0]["failure_type"] == "unknown_tool"
    assert failures[0]["tool"] == "weather.lookup"


def test_audio_demo_rejects_unknown_pipeline() -> None:
    client = _client()

    response = client.post(
        "/demo/audio",
        json={
            "audio_path": "data/fixtures/example.wav",
            "language": "en",
            "pipeline": "B",
            "execute_tool": True,
        },
    )

    assert response.status_code == 422
