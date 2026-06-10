from __future__ import annotations

import json


def repair_json_once(raw_output: str) -> str | None:
    """Extract one balanced JSON object from common model-output wrappers."""
    candidate = _extract_balanced_object(raw_output)
    if candidate is None:
        return None

    try:
        json.loads(candidate)
    except json.JSONDecodeError:
        return None
    return candidate


def _extract_balanced_object(text: str) -> str | None:
    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    in_string = False
    escaped = False

    for index, char in enumerate(text[start:], start=start):
        if escaped:
            escaped = False
            continue
        if char == "\\" and in_string:
            escaped = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]

    return None
