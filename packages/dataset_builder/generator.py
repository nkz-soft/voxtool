from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from packages.dataset_builder.models import BenchmarkExample, Language
from packages.dataset_builder.splits import assign_stratified_splits
from packages.tool_schema import ToolInvocation, execute_units_convert

ToolFamily = Literal["length", "mass", "temperature"]


@dataclass(frozen=True)
class ConversionTemplate:
    """Define one reusable unit-conversion prompt template."""

    family: ToolFamily
    value: float
    from_unit: str
    to_unit: str


CONVERSION_TEMPLATES: tuple[ConversionTemplate, ...] = (
    ConversionTemplate("length", 2, "kilometer", "meter"),
    ConversionTemplate("length", 120, "centimeter", "meter"),
    ConversionTemplate("length", 7, "meter", "millimeter"),
    ConversionTemplate("length", 1500, "millimeter", "meter"),
    ConversionTemplate("mass", 1, "kilogram", "gram"),
    ConversionTemplate("mass", 2, "pound", "ounce"),
    ConversionTemplate("mass", 500, "gram", "kilogram"),
    ConversionTemplate("mass", 16, "ounce", "pound"),
    ConversionTemplate("temperature", 0, "celsius", "fahrenheit"),
    ConversionTemplate("temperature", 212, "fahrenheit", "celsius"),
    ConversionTemplate("temperature", 25, "celsius", "fahrenheit"),
    ConversionTemplate("temperature", 68, "fahrenheit", "celsius"),
)

NO_TOOL_TEXTS: dict[Language, tuple[str, ...]] = {
    "en": (
        "What is the capital of New Zealand?",
        "Summarize why bilingual benchmarks are useful.",
        "Say hello in English.",
    ),
    "ru": (
        "Какая столица Новой Зеландии?",
        "Кратко объясни пользу двуязычных тестов.",
        "Поздоровайся по-русски.",
    ),
}


def generate_dataset(version: str) -> list[BenchmarkExample]:
    """Build the complete deterministic 240-example bilingual benchmark dataset."""
    records: list[dict[str, object]] = []
    for language in ("en", "ru"):
        for family in ("length", "mass", "temperature"):
            records.extend(_generate_tool_family(version, language, family))
        records.extend(_generate_no_tool(version, language))
    return _with_splits(records)


def _generate_tool_family(
    version: str,
    language: Language,
    family: ToolFamily,
) -> list[dict[str, object]]:
    templates = [
        template for template in CONVERSION_TEMPLATES if template.family == family
    ]
    records: list[dict[str, object]] = []
    for index in range(34):
        template = templates[index % len(templates)]
        sequence = index + 1
        invocation = ToolInvocation.model_validate(
            {
                "tool": "units.convert",
                "arguments": {
                    "value": template.value,
                    "from_unit": template.from_unit,
                    "to_unit": template.to_unit,
                },
            }
        )
        result = execute_units_convert(invocation)
        records.append(
            {
                "example_id": _example_id(version, language, family, sequence),
                "dataset_version": version,
                "language": language,
                "unit_family": family,
                "text": _conversion_text(language, template),
                "needs_tool": True,
                "expected_tool_call": invocation,
                "expected_final_answer": _conversion_answer(
                    language,
                    template,
                    result.rounded_display,
                ),
            }
        )
    return records


def _generate_no_tool(version: str, language: Language) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    texts = NO_TOOL_TEXTS[language]
    for index in range(18):
        sequence = index + 1
        records.append(
            {
                "example_id": _example_id(version, language, "none", sequence),
                "dataset_version": version,
                "language": language,
                "unit_family": "none",
                "text": texts[index % len(texts)],
                "needs_tool": False,
                "expected_tool_call": None,
                "expected_final_answer": _no_tool_answer(language),
            }
        )
    return records


def _with_splits(records: list[dict[str, object]]) -> list[BenchmarkExample]:
    examples: list[BenchmarkExample] = []
    strata = [
        (record["language"], record["needs_tool"], record["unit_family"])
        for record in records
    ]
    for record, split in assign_stratified_splits(records, strata):
        example_id = str(record["example_id"])
        examples.append(
            BenchmarkExample.model_validate(
                {
                    **record,
                    "split": split,
                    "audio_id": f"{example_id}-audio",
                }
            )
        )
    return examples


def _example_id(version: str, language: Language, family: str, sequence: int) -> str:
    return f"{version}-{language}-{family}-{sequence:04d}"


def _conversion_text(language: Language, template: ConversionTemplate) -> str:
    if language == "ru":
        return (
            f"Конвертируй {template.value:g} {template.from_unit} в {template.to_unit}."
        )
    return f"Convert {template.value:g} {template.from_unit} to {template.to_unit}."


def _conversion_answer(
    language: Language,
    template: ConversionTemplate,
    rounded_display: str,
) -> str:
    if language == "ru":
        return f"{template.value:g} {template.from_unit} равно {rounded_display}."
    return f"{template.value:g} {template.from_unit} is {rounded_display}."


def _no_tool_answer(language: Language) -> str:
    if language == "ru":
        return "Запрос не требует вызова инструмента."
    return "The request does not require a tool call."
