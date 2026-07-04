from __future__ import annotations

import os
import sys
from types import ModuleType
from typing import Any

from packages.model_runner.adapters.base import (
    clear_cuda_memory,
    generated_token_ids,
    release_runtime_objects,
)
from packages.model_runner.adapters.gemma import GemmaAdapter
from packages.model_runner.adapters.qwen import QwenAdapter
from packages.model_runner.adapters.voxtral import VoxtralAdapter


class _BatchEncoding:
    def __init__(self, input_ids: list[list[int]]) -> None:
        self.input_ids = input_ids


class _FakeTokenizer:
    def __init__(self) -> None:
        self.decoded_ids: list[int] | None = None

    def __call__(
        self, prompt: str, *, return_tensors: str
    ) -> dict[str, list[list[int]]]:
        assert prompt
        assert return_tensors == "pt"
        return {"input_ids": [[10, 11, 12]]}

    def decode(self, token_ids: list[int], *, skip_special_tokens: bool) -> str:
        assert skip_special_tokens
        self.decoded_ids = token_ids
        return "completion-json"


class _FakeCausalModel:
    def generate(self, **_: object) -> list[list[int]]:
        return [[10, 11, 12, 20, 21]]


class _FakeProcessor(_FakeTokenizer):
    chat_template_called = False

    @classmethod
    def from_pretrained(cls, model_name: str, *, token: str | None) -> _FakeProcessor:
        assert model_name == "dummy/voxtral"
        assert token is None
        return cls()

    def apply_chat_template(
        self,
        messages: list[dict[str, object]],
        *,
        return_tensors: str,
        return_dict: bool,
    ) -> dict[str, list[list[int]]]:
        assert messages[0]["role"] == "user"
        assert return_tensors == "pt"
        assert return_dict is True
        self.chat_template_called = True
        return {"input_ids": [[30, 31, 32]]}


class _FakeVoxtralModel:
    from_pretrained_called = False

    @classmethod
    def from_pretrained(cls, model_name: str, **kwargs: object) -> _FakeVoxtralModel:
        assert model_name == "dummy/voxtral"
        assert kwargs == {"token": None}
        cls.from_pretrained_called = True
        return cls()

    def generate(self, **_: object) -> list[list[int]]:
        return [[30, 31, 32, 40, 41]]


class _FakeRuntimeModel:
    def __init__(self) -> None:
        self.cpu_called = False

    def cpu(self) -> None:
        self.cpu_called = True


def test_generated_token_ids_removes_prompt_prefix_from_mapping_inputs() -> None:
    output_ids = [10, 11, 12, 20, 21]
    inputs = {"input_ids": [[10, 11, 12]]}

    assert generated_token_ids(output_ids, inputs) == [20, 21]


def test_generated_token_ids_removes_prompt_prefix_from_attribute_inputs() -> None:
    output_ids = [10, 11, 12, 20, 21]
    inputs = _BatchEncoding([[10, 11, 12]])

    assert generated_token_ids(output_ids, inputs) == [20, 21]


def test_generated_token_ids_keeps_output_when_prompt_length_is_unknown() -> None:
    output_ids = [20, 21]

    assert generated_token_ids(output_ids, object()) == output_ids


def test_release_runtime_objects_moves_cached_model_to_cpu() -> None:
    model = _FakeRuntimeModel()

    release_runtime_objects((_FakeTokenizer(), model))

    assert model.cpu_called


def test_clear_cuda_memory_sets_fragmentation_allocator_config(
    monkeypatch: Any,
) -> None:
    monkeypatch.delenv("PYTORCH_CUDA_ALLOC_CONF", raising=False)

    clear_cuda_memory()

    assert "expandable_segments:True" in os.environ["PYTORCH_CUDA_ALLOC_CONF"]


def test_qwen_generate_text_decodes_only_generated_tokens() -> None:
    tokenizer = _FakeTokenizer()
    adapter = QwenAdapter(model_name="dummy/qwen")
    adapter._runtime = (tokenizer, _FakeCausalModel())

    response = adapter.generate_text("prompt")

    assert response.error is None
    assert response.raw_output == "completion-json"
    assert tokenizer.decoded_ids == [20, 21]


def test_gemma_generate_text_decodes_only_generated_tokens() -> None:
    tokenizer = _FakeTokenizer()
    adapter = GemmaAdapter(model_name="dummy/gemma")
    adapter._runtime = (tokenizer, _FakeCausalModel())

    response = adapter.generate_text("prompt")

    assert response.error is None
    assert response.raw_output == "completion-json"
    assert tokenizer.decoded_ids == [20, 21]


def test_voxtral_uses_conditional_generation_and_decodes_completion(
    monkeypatch: Any,
) -> None:
    fake_transformers: Any = ModuleType("transformers")
    fake_transformers.AutoProcessor = _FakeProcessor
    fake_transformers.VoxtralForConditionalGeneration = _FakeVoxtralModel
    monkeypatch.setitem(sys.modules, "transformers", fake_transformers)
    _FakeVoxtralModel.from_pretrained_called = False

    adapter = VoxtralAdapter(model_name="dummy/voxtral")
    response = adapter.generate_text("prompt")
    processor, _model = adapter._runtime

    assert response.error is None
    assert response.raw_output == "completion-json"
    assert isinstance(processor, _FakeProcessor)
    assert processor.chat_template_called
    assert processor.decoded_ids == [40, 41]
    assert _FakeVoxtralModel.from_pretrained_called
