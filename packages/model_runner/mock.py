from __future__ import annotations

import json
import re
from collections.abc import Mapping

from packages.model_runner.base import ModelOutput


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
        pattern = re.compile(
            r"convert\s+(?P<value>-?\d+(?:\.\d+)?)\s+"
            r"(?P<from_unit>[a-z]+)s?\s+to\s+"
            r"(?P<to_unit>[a-z]+)s?",
            re.IGNORECASE,
        )
        match = pattern.search(prompt)
        if match is None:
            return None
        value = float(match.group("value"))
        if value.is_integer():
            value = int(value)
        return value, _singular_unit(match.group("from_unit")), _singular_unit(
            match.group("to_unit")
        )

    def _final_answer(self, value: float, from_unit: str, to_unit: str) -> str:
        if value == 2 and from_unit == "kilometer" and to_unit == "meter":
            return "2 kilometers is 2000 meters."
        return f"Converted {value:g} {from_unit} to {to_unit}."


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
