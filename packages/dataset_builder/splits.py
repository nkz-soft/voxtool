from __future__ import annotations

from collections import defaultdict
from collections.abc import Hashable, Sequence
from typing import TypeVar

from sklearn.model_selection import train_test_split  # type: ignore[import-untyped]

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
    """Assign train/validation/test labels with sklearn within each stratum.

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
    train_items, temp_items = train_test_split(
        list(items),
        train_size=counts["train"],
        test_size=counts["validation"] + counts["test"],
        random_state=RANDOM_STATE,
        shuffle=True,
    )
    validation_items, test_items = train_test_split(
        temp_items,
        train_size=counts["validation"],
        test_size=counts["test"],
        random_state=RANDOM_STATE,
        shuffle=True,
    )

    assigned: list[tuple[T, Split]] = []
    assigned.extend((item, "train") for item in train_items)
    assigned.extend((item, "validation") for item in validation_items)
    assigned.extend((item, "test") for item in test_items)
    return assigned
