"""Script entrypoint for the dataset generation CLI command group."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    """Run the dataset generation CLI app."""
    from apps.cli.dataset import app

    app()


if __name__ == "__main__":
    main()
