from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from packages.dataset_builder.models import BenchmarkExample


def write_jsonl(path: Path, examples: Iterable[BenchmarkExample]) -> int:
    """Write benchmark examples as UTF-8 JSONL and return the record count."""
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as file:
        for example in examples:
            file.write(json.dumps(example.model_dump(mode="json"), ensure_ascii=False))
            file.write("\n")
            count += 1
    return count


def read_jsonl(path: Path) -> list[BenchmarkExample]:
    """Read benchmark examples from JSONL and validate each record.

    Raises ValueError when a non-empty line is not valid JSON. Pydantic
    validation errors are allowed to propagate with field-level details.
    """
    examples: list[BenchmarkExample] = []
    with path.open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                payload = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at line {line_number}: {exc}") from exc
            examples.append(BenchmarkExample.model_validate(payload))
    return examples
