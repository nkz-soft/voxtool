from collections import Counter

from packages.dataset_builder import generate_dataset


def test_generated_dataset_has_required_balance_and_fields() -> None:
    examples = generate_dataset(version="v1")

    assert len(examples) == 240
    assert len({example.example_id for example in examples}) == 240
    assert len({example.audio_id for example in examples}) == 240

    languages = Counter(example.language for example in examples)
    assert languages == {"en": 120, "ru": 120}

    no_tool_by_language = Counter(
        example.language for example in examples if not example.needs_tool
    )
    assert no_tool_by_language == {"en": 18, "ru": 18}

    tool_by_family_language = Counter(
        (example.language, example.unit_family)
        for example in examples
        if example.needs_tool
    )
    assert tool_by_family_language == {
        ("en", "length"): 34,
        ("en", "mass"): 34,
        ("en", "temperature"): 34,
        ("ru", "length"): 34,
        ("ru", "mass"): 34,
        ("ru", "temperature"): 34,
    }

    for example in examples:
        assert example.dataset_version == "v1"
        assert example.text
        assert example.expected_final_answer
        assert example.audio_id == f"{example.example_id}-audio"
        if example.needs_tool:
            assert example.expected_tool_call is not None
            assert example.expected_tool_call.tool == "units.convert"
        else:
            assert example.unit_family == "none"
            assert example.expected_tool_call is None


def test_dataset_generation_is_deterministic() -> None:
    first = [example.model_dump(mode="json") for example in generate_dataset("v1")]
    second = [example.model_dump(mode="json") for example in generate_dataset("v1")]

    assert first == second
