from __future__ import annotations

import json
import re
from collections.abc import Mapping

from packages.model_runner.base import ModelOutput

# English: "convert 2 kilometers to meters".
_ENGLISH_CONVERSION = re.compile(
    r"convert\s+(?P<value>-?\d+(?:\.\d+)?)\s+"
    r"(?P<from_unit>[a-z]+)s?\s+to\s+"
    r"(?P<to_unit>[a-z]+)s?",
    re.IGNORECASE,
)

# Russian: "сконвертируй/переведи/конвертируй 2 километра в метры". Russian nouns
# are inflected for case, so the unit tokens are matched by stem in
# ``_russian_unit`` rather than enumerated here. The value may use a comma
# decimal separator, normalized in ``_normalize_conversion``.
_RUSSIAN_CONVERSION = re.compile(
    r"(?:сконвертируй(?:те)?|сконвертировать|конвертируй(?:те)?|"
    r"переведи(?:те)?|перевести|преобразуй(?:те)?)\s+"
    r"(?P<value>-?\d+(?:[.,]\d+)?)\s+"
    r"(?P<from_unit>[а-яё]+)\s+в\s+"
    r"(?P<to_unit>[а-яё]+)",
    re.IGNORECASE,
)


class MockModelAdapter:
    """Deterministic text adapter for smoke tests and local benchmark runs."""

    name = "MockModelAdapter"

    def __init__(self, response_overrides: Mapping[str, str] | None = None) -> None:
        self.response_overrides = dict(response_overrides or {})

    def generate_text(self, prompt: str) -> ModelOutput:
        """Return a deterministic model envelope or configured override."""
        for marker, raw_output in self.response_overrides.items():
            if marker in prompt:
                return ModelOutput(raw_output=raw_output, adapter_name=self.name)

        payload = self._build_payload(prompt)
        return ModelOutput(
            raw_output=json.dumps(payload, ensure_ascii=False),
            adapter_name=self.name,
        )

    def _build_payload(self, prompt: str) -> dict[str, object]:
        conversion = self._extract_conversion(prompt)
        if conversion is None:
            return {
                "needs_tool": False,
                "tool_call": None,
                "final_answer": "No conversion needed.",
            }

        value, from_unit, to_unit = conversion
        return {
            "needs_tool": True,
            "tool_call": {
                "tool": "units.convert",
                "arguments": {
                    "value": value,
                    "from_unit": from_unit,
                    "to_unit": to_unit,
                },
            },
            "final_answer": self._final_answer(value, from_unit, to_unit),
        }

    def _extract_conversion(self, prompt: str) -> tuple[float, str, str] | None:
        match = _ENGLISH_CONVERSION.search(prompt)
        if match is not None:
            return _normalize_conversion(
                match.group("value"),
                _singular_unit(match.group("from_unit")),
                _singular_unit(match.group("to_unit")),
            )

        match = _RUSSIAN_CONVERSION.search(prompt)
        if match is not None:
            from_unit = _russian_unit(match.group("from_unit"))
            to_unit = _russian_unit(match.group("to_unit"))
            if from_unit is not None and to_unit is not None:
                return _normalize_conversion(
                    match.group("value"), from_unit, to_unit
                )
        return None

    def _final_answer(self, value: float, from_unit: str, to_unit: str) -> str:
        if value == 2 and from_unit == "kilometer" and to_unit == "meter":
            return "2 kilometers is 2000 meters."
        return f"Converted {value:g} {from_unit} to {to_unit}."


def _normalize_conversion(
    value_text: str, from_unit: str, to_unit: str
) -> tuple[float, str, str]:
    """Parse a numeric value (accepting comma decimals) into a clean int/float."""
    value = float(value_text.replace(",", "."))
    if value.is_integer():
        value = int(value)
    return (value, from_unit, to_unit)


# Russian unit stems mapped to canonical English unit names, ordered so the most
# specific stem wins (e.g. "килограмм" before "грамм", "километр" before "метр").
_RUSSIAN_UNIT_STEMS: tuple[tuple[str, str], ...] = (
    ("килограмм", "kilogram"),
    ("грамм", "gram"),
    ("километр", "kilometer"),
    ("сантиметр", "centimeter"),
    ("миллиметр", "millimeter"),
    ("метр", "meter"),
    ("фунт", "pound"),
    ("унци", "ounce"),
    ("цельси", "celsius"),
    ("фаренгейт", "fahrenheit"),
)


def _russian_unit(token: str) -> str | None:
    """Map an inflected Russian unit word to its canonical English unit name."""
    lowered = token.lower()
    for stem, canonical in _RUSSIAN_UNIT_STEMS:
        if lowered.startswith(stem):
            return canonical
    return None


def _singular_unit(unit: str) -> str:
    aliases = {
        "meters": "meter",
        "meter": "meter",
        "kilometers": "kilometer",
        "kilometer": "kilometer",
        "centimeters": "centimeter",
        "centimeter": "centimeter",
        "millimeters": "millimeter",
        "millimeter": "millimeter",
        "grams": "gram",
        "gram": "gram",
        "kilograms": "kilogram",
        "kilogram": "kilogram",
        "pounds": "pound",
        "pound": "pound",
        "ounces": "ounce",
        "ounce": "ounce",
        "celsius": "celsius",
        "fahrenheit": "fahrenheit",
    }
    return aliases.get(unit.lower(), unit.lower())
