from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field

from packages.model_runner.adapters.base import AdapterCapabilities, ModelAdapter
from packages.model_runner.adapters.gemma import GemmaAdapter
from packages.model_runner.adapters.mock import MockModelAdapter
from packages.model_runner.adapters.qwen import QwenAdapter
from packages.model_runner.adapters.voxtral import VoxtralAdapter

# Map of stable adapter IDs to their import-safe adapter classes. Constructing a
# class does not load a model; weights are fetched lazily on first generation.
ADAPTER_CLASSES: dict[str, type] = {
    "mock": MockModelAdapter,
    "voxtral": VoxtralAdapter,
    "qwen": QwenAdapter,
    "gemma": GemmaAdapter,
}

# Default config file per real adapter, resolved relative to the repo root.
_DEFAULT_CONFIG_PATHS: dict[str, str] = {
    "voxtral": "configs/models/voxtral.yaml",
    "qwen": "configs/models/qwen.yaml",
    "gemma": "configs/models/gemma.yaml",
}

_REPO_ROOT = Path(__file__).resolve().parents[2]


class AdapterConfig(BaseModel):
    """Parsed model-adapter config describing how to build an adapter.

    The config declares the model and its declared capabilities only; it must not
    trigger a model download. ``eager_download`` is required to be ``False`` so
    that ordinary CI config validation can assert no eager loading is requested.
    """

    model_config = ConfigDict(extra="forbid")

    adapter_id: str = Field(min_length=1)
    model_family: str = Field(min_length=1)
    model_name: str = Field(min_length=1)
    inference_profile: str = "base"
    eager_download: bool = False
    runtime: dict[str, Any] = Field(default_factory=dict)
    capabilities: AdapterCapabilities = Field(default_factory=AdapterCapabilities)
    generation: dict[str, Any] = Field(default_factory=dict)


def load_adapter_config(path: str | Path) -> AdapterConfig:
    """Load and validate a model-adapter config from a YAML file."""
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}
    config = AdapterConfig.model_validate(data)
    if config.eager_download:
        raise ValueError(
            f"Adapter config {config_path} sets eager_download: true; "
            "ordinary runs must not download models eagerly."
        )
    return config


def available_adapters() -> list[str]:
    """Return the list of registered adapter IDs."""
    return sorted(ADAPTER_CLASSES)


def default_config_path(adapter_id: str) -> Path | None:
    """Return the default config path for a real adapter, if one exists."""
    relative = _DEFAULT_CONFIG_PATHS.get(adapter_id)
    return _REPO_ROOT / relative if relative is not None else None


def build_adapter(
    adapter_id: str,
    *,
    config_path: str | Path | None = None,
) -> ModelAdapter:
    """Build an import-safe adapter instance from its config.

    The returned adapter satisfies the :class:`ModelAdapter` protocol. No model
    is downloaded here; real weights load lazily on the first ``generate_text``
    call. The ``mock`` adapter needs no config and is built directly.
    """
    if adapter_id not in ADAPTER_CLASSES:
        raise ValueError(
            f"Unknown adapter_id {adapter_id!r}; "
            f"available adapters: {', '.join(available_adapters())}."
        )

    if adapter_id == "mock":
        return MockModelAdapter()

    resolved = (
        Path(config_path)
        if config_path is not None
        else default_config_path(adapter_id)
    )
    if resolved is None:
        raise ValueError(f"No config path available for adapter_id {adapter_id!r}.")

    config = load_adapter_config(resolved)
    adapter_cls = ADAPTER_CLASSES[adapter_id]
    adapter: ModelAdapter = adapter_cls(
        adapter_id=config.adapter_id,
        model_name=config.model_name,
        inference_profile=config.inference_profile,
        generation=config.generation,
    )
    return adapter
