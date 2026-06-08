import ast
from pathlib import Path

FORBIDDEN_IMPORTS = {
    "packages.tool_schema.executor",
    "packages.tool_schema.units",
}


def test_pipeline_runner_does_not_import_concrete_tools() -> None:
    pipeline_root = Path("packages/pipeline_runner")
    violations: list[str] = []

    for path in pipeline_root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in FORBIDDEN_IMPORTS:
                        violations.append(f"{path}: import {alias.name}")
            if isinstance(node, ast.ImportFrom) and node.module in FORBIDDEN_IMPORTS:
                violations.append(f"{path}: from {node.module} import ...")

    assert violations == []
