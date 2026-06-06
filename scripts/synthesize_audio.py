from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Synthesize audio fixture stubs.")
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    (output / "manifest.json").write_text(
        json.dumps({"dataset": args.dataset, "audio": []}, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
