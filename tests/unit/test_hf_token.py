import pytest
from packages.model_runner.adapters.base import resolve_hf_token


def test_resolve_hf_token_returns_none_when_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("HF_TOKEN", raising=False)
    monkeypatch.delenv("HUGGING_FACE_HUB_TOKEN", raising=False)

    assert resolve_hf_token() is None


def test_resolve_hf_token_prefers_hf_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("HF_TOKEN", "primary")
    monkeypatch.setenv("HUGGING_FACE_HUB_TOKEN", "secondary")

    assert resolve_hf_token() == "primary"


def test_resolve_hf_token_falls_back_to_hub_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("HF_TOKEN", raising=False)
    monkeypatch.setenv("HUGGING_FACE_HUB_TOKEN", "secondary")

    assert resolve_hf_token() == "secondary"
