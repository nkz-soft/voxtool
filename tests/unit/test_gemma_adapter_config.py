from __future__ import annotations

from packages.model_runner.adapters.base import AdapterCapabilities, ModelAdapter
from packages.model_runner.adapters.gemma import GemmaAdapter
from packages.model_runner.registry import default_config_path, load_adapter_config


def test_gemma_adapter_imports_without_heavy_deps() -> None:
    adapter = GemmaAdapter(model_name="dummy/gemma")

    assert isinstance(adapter, ModelAdapter)
    assert adapter.adapter_id == "gemma"


def test_gemma_capabilities_are_text_only_tool_calling() -> None:
    capabilities = GemmaAdapter().capabilities

    assert isinstance(capabilities, AdapterCapabilities)
    assert capabilities.supports_text_input
    assert capabilities.supports_tool_call_output
    assert not capabilities.supports_audio_input
    assert capabilities.satisfies_pipeline("A")
    assert capabilities.satisfies_pipeline("D")
    assert not capabilities.satisfies_pipeline("C")


def test_gemma_config_loads_without_eager_download() -> None:
    config_path = default_config_path("gemma")
    assert config_path is not None and config_path.exists()

    config = load_adapter_config(config_path)

    assert config.adapter_id == "gemma"
    assert config.model_family == "gemma"
    assert config.model_name
    assert config.eager_download is False
    assert config.capabilities.supports_lora
    assert config.capabilities.supports_quantization
