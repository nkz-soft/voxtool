import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

DEFAULT_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "configs"
    / "tools"
    / "model-output.schema.json"
)


def load_model_output_schema(path: str | Path | None = None) -> dict[str, Any]:
    schema_path = Path(path) if path is not None else DEFAULT_SCHEMA_PATH
    with schema_path.open(encoding="utf-8") as schema_file:
        schema = json.load(schema_file)

    Draft202012Validator.check_schema(schema)
    return schema


def validate_model_output(
    instance: Mapping[str, Any],
    *,
    schema: Mapping[str, Any] | None = None,
) -> None:
    active_schema = dict(schema) if schema is not None else load_model_output_schema()
    validator = Draft202012Validator(active_schema)
    errors = sorted(validator.iter_errors(instance), key=lambda error: list(error.path))
    if errors:
        messages = [
            f"{'/'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
            for error in errors
        ]
        raise ValueError("; ".join(messages))
