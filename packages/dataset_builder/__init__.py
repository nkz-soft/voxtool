"""Synthetic bilingual benchmark dataset generation."""

from packages.dataset_builder.generator import generate_dataset
from packages.dataset_builder.io import read_jsonl, write_jsonl
from packages.dataset_builder.models import BenchmarkExample, GenerationMetadata

__all__ = [
    "BenchmarkExample",
    "GenerationMetadata",
    "generate_dataset",
    "read_jsonl",
    "write_jsonl",
]
