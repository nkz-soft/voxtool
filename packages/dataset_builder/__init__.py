"""Synthetic bilingual benchmark dataset generation."""

from typing import Any

from packages.dataset_builder.models import BenchmarkExample, GenerationMetadata

__all__ = [
    "BenchmarkExample",
    "GenerationMetadata",
    "generate_dataset",
    "read_jsonl",
    "write_jsonl",
]


def __getattr__(name: str) -> Any:
    if name == "generate_dataset":
        from packages.dataset_builder.generator import generate_dataset

        return generate_dataset
    if name in {"read_jsonl", "write_jsonl"}:
        from packages.dataset_builder.io import read_jsonl, write_jsonl

        return {"read_jsonl": read_jsonl, "write_jsonl": write_jsonl}[name]
    raise AttributeError(name)
