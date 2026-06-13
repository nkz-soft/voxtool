from __future__ import annotations

from pathlib import Path

import pytest
from packages.model_runner.adapters.base import (
    AdapterCapabilities,
    ModelAdapter,
    ModelResponse,
)
from packages.model_runner.adapters.gemma import GemmaAdapter
from packages.model_runner.adapters.mock import MockModelAdapter
from packages.model_runner.adapters.qwen import QwenAdapter
from packages.model_runner.adapters.voxtral import VoxtralAdapter
from packages.model_runner.registry import (
    available_adapters,
    build_adapter,
    load_adapter_config,
)


def _real_adapters() -> list[ModelAdapter]:
    return [
        VoxtralAdapter(model_name="dummy/voxtral"),
        QwenAdapter(model_name="dummy/qwen"),
        GemmaAdapter(model_name="dummy/gemma"),
    ]


@pytest.mark.parametrize("adapter", [MockModelAdapter(), *_real_adapters()])
def test_adapters_satisfy_model_adapter_protocol(adapter: ModelAdapter) -> None:
    assert isinstance(adapter, ModelAdapter)
    assert isinstance(adapter.adapter_id, str) and adapter.adapter_id
    assert isinstance(adapter.capabilities, AdapterCapabilities)


def test_mock_adapter_returns_canonical_model_response() -> None:
    adapter = MockModelAdapter()

    response = adapter.generate_text("Convert 2 kilometers to meters.")

    assert isinstance(response, ModelResponse)
    assert response.error is None
    assert "units.convert" in response.raw_output


def test_real_adapter_generate_text_surfaces_missing_deps_as_error() -> None:
    # No heavy deps in CI: generation must not raise; it returns an error field.
    adapter = QwenAdapter(model_name="dummy/qwen")

    response = adapter.generate_text("hello")

    assert isinstance(response, ModelResponse)
    assert response.error is not None


def test_registry_lists_and_builds_adapters() -> None:
    assert available_adapters() == ["gemma", "mock", "qwen", "voxtral"]

    for adapter_id in ("voxtral", "qwen", "gemma"):
        adapter = build_adapter(adapter_id)
        assert adapter.adapter_id == adapter_id
        assert isinstance(adapter, ModelAdapter)


def test_registry_rejects_unknown_adapter() -> None:
    with pytest.raises(ValueError, match="Unknown adapter_id"):
        build_adapter("does-not-exist")


def test_registry_rejects_eager_download_config(tmp_path: Path) -> None:
    config = tmp_path / "bad.yaml"
    config.write_text(
        "adapter_id: qwen\n"
        "model_family: qwen\n"
        "model_name: dummy/qwen\n"
        "eager_download: true\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="eager_download"):
        load_adapter_config(config)
