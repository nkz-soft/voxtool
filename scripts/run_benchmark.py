from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic smoke benchmark.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--model", default="mock")
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    metrics = {
        "config": args.config,
        "model": args.model,
        "limit": args.limit,
        "pipelines": ["A", "B", "C", "D"],
        "examples_evaluated": 0,
    }
    (output / "metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
