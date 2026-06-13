from __future__ import annotations

from typing import Any

from packages.model_runner.adapters.base import AdapterCapabilities, ModelResponse
from packages.model_runner.mock import MockModelAdapter as _LegacyMockModelAdapter


def _default_capabilities() -> AdapterCapabilities:
    return AdapterCapabilities(
        supports_text_input=True,
        supports_tool_call_output=True,
        supported_pipelines=["A", "D"],
    )


class MockModelAdapter:
    """Deterministic adapter implementing the advanced ``ModelAdapter`` contract.

    Unlike the legacy text adapter, this mock exposes an ``adapter_id`` and
    declared ``capabilities`` and returns a :class:`ModelResponse`. It is the
    canonical mock used by adapter contract tests and mock-backed pipeline runs
    so the registry and runner can exercise the real-adapter code path without
    downloading any model. Tool-call envelopes are produced by delegating to the
    legacy deterministic mock so existing fixtures keep working.
    """

    def __init__(
        self,
        *,
        adapter_id: str = "mock",
        capabilities: AdapterCapabilities | None = None,
        response_overrides: dict[str, str] | None = None,
    ) -> None:
        self._adapter_id = adapter_id
        self._capabilities = capabilities or _default_capabilities()
        self._legacy = _LegacyMockModelAdapter(response_overrides)

    @property
    def adapter_id(self) -> str:
        """Return the stable adapter identifier stored in run artifacts."""
        return self._adapter_id

    @property
    def capabilities(self) -> AdapterCapabilities:
        """Return the adapter's declared capabilities."""
        return self._capabilities

    def generate_text(
        self, prompt: str, config: dict[str, Any] | None = None
    ) -> ModelResponse:
        """Return a deterministic canonical JSON envelope as raw output."""
        legacy_output = self._legacy.generate_text(prompt)
        return ModelResponse(
            raw_output=legacy_output.raw_output,
            metadata={"adapter_name": legacy_output.adapter_name},
        )
