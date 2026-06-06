from __future__ import annotations

from pathlib import Path


def test_required_scaffold_paths_exist() -> None:
    root = Path(__file__).resolve().parents[2]
    required_paths = [
        root / "apps" / "api" / "main.py",
        root / "apps" / "cli" / "__main__.py",
        root / "configs" / "experiments" / "smoke.yml",
        root / "scripts" / "run_benchmark.py",
    ]

    assert all(path.exists() for path in required_paths)
