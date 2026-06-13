from packages.model_runner.adapters import (
    AdapterCapabilities,
    SkippedCapability,
    evaluate_capability,
)


def _text_only_capabilities() -> AdapterCapabilities:
    return AdapterCapabilities(
        supports_text_input=True,
        supports_tool_call_output=True,
        supported_pipelines=["A", "D"],
    )


def _audio_capabilities() -> AdapterCapabilities:
    return AdapterCapabilities(
        supports_text_input=True,
        supports_audio_input=True,
        supports_transcript_output=True,
        supports_tool_call_output=True,
        supported_pipelines=["A", "C", "D"],
    )


def test_text_adapter_satisfies_text_pipelines() -> None:
    capabilities = _text_only_capabilities()

    assert capabilities.satisfies_pipeline("A")
    assert capabilities.satisfies_pipeline("D")
    assert capabilities.missing_for_pipeline("A") == []


def test_text_adapter_cannot_satisfy_audio_pipeline() -> None:
    capabilities = _text_only_capabilities()

    missing = capabilities.missing_for_pipeline("C")

    assert not capabilities.satisfies_pipeline("C")
    assert "supports_audio_input" in missing
    assert "supports_transcript_output" in missing
    assert "supported_pipelines" in missing


def test_evaluate_capability_returns_none_when_supported() -> None:
    result = evaluate_capability(
        adapter_id="qwen",
        capabilities=_text_only_capabilities(),
        pipeline="A",
    )

    assert result is None


def test_evaluate_capability_returns_structured_skip_when_unsupported() -> None:
    result = evaluate_capability(
        adapter_id="qwen",
        capabilities=_text_only_capabilities(),
        pipeline="C",
    )

    assert isinstance(result, SkippedCapability)
    assert result.adapter_id == "qwen"
    assert result.pipeline == "C"
    assert "supports_audio_input" in result.missing_capabilities
    assert "qwen" in result.reason


def test_capability_membership_alone_is_not_enough() -> None:
    capabilities = AdapterCapabilities(
        supports_text_input=True,
        supports_tool_call_output=False,
        supported_pipelines=["A"],
    )

    assert capabilities.missing_for_pipeline("A") == ["supports_tool_call_output"]


def test_audio_adapter_satisfies_all_pipelines() -> None:
    capabilities = _audio_capabilities()

    assert capabilities.satisfies_pipeline("A")
    assert capabilities.satisfies_pipeline("C")
    assert capabilities.satisfies_pipeline("D")
