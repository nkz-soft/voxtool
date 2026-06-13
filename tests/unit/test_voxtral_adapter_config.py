from __future__ import annotations

from packages.model_runner.adapters.base import AdapterCapabilities, ModelAdapter
from packages.model_runner.adapters.voxtral import VoxtralAdapter
from packages.model_runner.registry import default_config_path, load_adapter_config


def test_voxtral_adapter_imports_without_heavy_deps() -> None:
    adapter = VoxtralAdapter(model_name="dummy/voxtral")

    assert isinstance(adapter, ModelAdapter)
    assert adapter.adapter_id == "voxtral"


def test_voxtral_capabilities_cover_audio_pipelines() -> None:
    capabilities = VoxtralAdapter().capabilities

    assert isinstance(capabilities, AdapterCapabilities)
    assert capabilities.supports_audio_input
    assert capabilities.supports_transcript_output
    assert capabilities.satisfies_pipeline("A")
    assert capabilities.satisfies_pipeline("C")
    assert capabilities.satisfies_pipeline("D")


def test_voxtral_config_loads_without_eager_download() -> None:
    config_path = default_config_path("voxtral")
    assert config_path is not None and config_path.exists()

    config = load_adapter_config(config_path)

    assert config.adapter_id == "voxtral"
    assert config.model_family == "voxtral"
    assert config.model_name
    assert config.eager_download is False
    assert config.capabilities.supports_audio_input
