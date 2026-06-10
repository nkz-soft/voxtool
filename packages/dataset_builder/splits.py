from __future__ import annotations

import random
from collections import defaultdict
from collections.abc import Hashable, Sequence
from typing import TypeVar

from packages.dataset_builder.models import Split

T = TypeVar("T")
RANDOM_STATE = 42


def split_counts(total: int) -> dict[Split, int]:
    """Return deterministic 70/15/15 split counts for a stratum size."""
    train = round(total * 0.70)
    validation = round(total * 0.15)
    test = total - train - validation
    return {"train": train, "validation": validation, "test": test}


def assign_stratified_splits(
    items: Sequence[T],
    strata: Sequence[Hashable],
) -> list[tuple[T, Split]]:
    """Assign train/validation/test labels deterministically within each stratum.

    The returned list preserves the input item order. Raises ValueError when the
    item and stratum sequences do not have matching lengths.
    """
    if len(items) != len(strata):
        raise ValueError("items and strata must have the same length")

    grouped: dict[Hashable, list[T]] = defaultdict(list)
    for item, stratum in zip(items, strata, strict=True):
        grouped[stratum].append(item)

    split_by_identity: dict[int, Split] = {}
    for group in grouped.values():
        for item, split in _split_group(group):
            split_by_identity[id(item)] = split

    return [(item, split_by_identity[id(item)]) for item in items]


def _split_group(items: Sequence[T]) -> list[tuple[T, Split]]:
    counts = split_counts(len(items))
    shuffled = list(items)
    random.Random(RANDOM_STATE).shuffle(shuffled)

    train_end = counts["train"]
    validation_end = train_end + counts["validation"]
    train_items = shuffled[:train_end]
    validation_items = shuffled[train_end:validation_end]
    test_items = shuffled[validation_end:]

    assigned: list[tuple[T, Split]] = []
    assigned.extend((item, "train") for item in train_items)
    assigned.extend((item, "validation") for item in validation_items)
    assigned.extend((item, "test") for item in test_items)
    return assigned
