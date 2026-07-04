from __future__ import annotations

import json


def repair_json_once(raw_output: str) -> str | None:
    """Extract one balanced JSON envelope from common model-output wrappers."""
    candidate = _select_json_object(raw_output)
    if candidate is None:
        return None

    try:
        json.loads(candidate)
    except json.JSONDecodeError:
        return None
    return candidate


def _select_json_object(text: str) -> str | None:
    candidates = list(_extract_balanced_objects(text))
    if not candidates:
        return None

    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if _looks_like_model_output_envelope(parsed):
            return candidate
    return candidates[0]


def _extract_balanced_objects(text: str) -> list[str]:
    objects: list[str] = []

    for start, char in enumerate(text):
        if char != "{":
            continue

        depth = 0
        in_string = False
        escaped = False

        for index, current in enumerate(text[start:], start=start):
            if escaped:
                escaped = False
                continue
            if current == "\\" and in_string:
                escaped = True
                continue
            if current == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if current == "{":
                depth += 1
            elif current == "}":
                depth -= 1
                if depth == 0:
                    objects.append(text[start : index + 1])
                    break

    return objects


def _looks_like_model_output_envelope(parsed: object) -> bool:
    if not isinstance(parsed, dict):
        return False
    return {"needs_tool", "tool_call", "final_answer"}.issubset(parsed)
