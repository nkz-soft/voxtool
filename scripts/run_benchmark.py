from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Literal, cast

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    """Parse script arguments and run the benchmark dispatcher."""
    from packages.pipeline_runner.runner import run_benchmark
    from packages.tool_schema.providers import ToolExecutor
    from packages.tool_schema.units import default_tool_registry

    parser = argparse.ArgumentParser(description="Run a benchmark pipeline.")
    parser.add_argument("--dataset", default=None)
    parser.add_argument("--audio-metadata", default=None)
    parser.add_argument("--pipeline", choices=["A", "B", "C", "D"], default="A")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--model", default="mock")
    parser.add_argument("--output", required=True)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    audio_pipeline = args.pipeline in ("B", "C", "D")
    input_path = args.audio_metadata if audio_pipeline else args.dataset
    if input_path is None:
        option = "--audio-metadata" if audio_pipeline else "--dataset"
        parser.error(f"{option} is required for Pipeline {args.pipeline}")

    registry = default_tool_registry()
    run_benchmark(
        pipeline=cast(Literal["A", "B", "C", "D"], args.pipeline),
        dataset_path=Path(input_path),
        output_path=Path(args.output),
        run_id=args.run_id,
        registry=registry,
        executor=ToolExecutor(registry),
        model=cast(Literal["mock"], args.model),
        limit=args.limit,
    )


if __name__ == "__main__":
    main()
