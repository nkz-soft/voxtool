from collections import Counter, defaultdict

from packages.dataset_builder import generate_dataset


def test_splits_are_deterministic_and_stratified() -> None:
    examples = generate_dataset(version="v1")

    split_by_id = {example.example_id: example.split for example in examples}
    regenerated = generate_dataset(version="v1")
    assert split_by_id == {example.example_id: example.split for example in regenerated}

    strata: dict[tuple[str, bool, str], Counter[str]] = defaultdict(Counter)
    for example in examples:
        strata[(example.language, example.needs_tool, example.unit_family)][
            example.split
        ] += 1

    for (language, needs_tool, unit_family), split_counts in strata.items():
        expected = {"train": 24, "validation": 5, "test": 5}
        if not needs_tool and unit_family == "none":
            expected = {"train": 13, "validation": 3, "test": 2}
        assert split_counts == expected, (language, needs_tool, unit_family)


def test_overall_split_counts_are_stable() -> None:
    examples = generate_dataset(version="v1")

    assert Counter(example.split for example in examples) == {
        "train": 170,
        "validation": 36,
        "test": 34,
    }
