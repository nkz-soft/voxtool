.PHONY: install lint typecheck test benchmark-smoke

install:
	uv sync --all-groups

lint:
	uv run ruff check .
	uv run ruff format --check .

typecheck:
	uv run mypy

test:
	uv run pytest

benchmark-smoke:
	uv run python scripts/synthesize_audio.py --dataset data/fixtures/examples.small.jsonl --output reports/smoke/audio
	uv run python scripts/run_benchmark.py --pipeline A --dataset data/fixtures/examples.small.jsonl --run-id smoke --model mock --limit 30 --output reports/smoke/pipeline-a.jsonl
	uv run python scripts/run_benchmark.py --pipeline B --audio-metadata reports/smoke/audio/audio.jsonl --run-id smoke --model mock --limit 30 --output reports/smoke/pipeline-b.jsonl
	uv run python scripts/run_benchmark.py --pipeline C --audio-metadata reports/smoke/audio/audio.jsonl --run-id smoke --model mock --limit 30 --output reports/smoke/pipeline-c.jsonl
	uv run python scripts/run_benchmark.py --pipeline D --audio-metadata reports/smoke/audio/audio.jsonl --run-id smoke --model mock --limit 30 --output reports/smoke/pipeline-d.jsonl
	uv run python scripts/build_report.py --dataset data/fixtures/examples.small.jsonl --run reports/smoke/pipeline-a.jsonl --run reports/smoke/pipeline-b.jsonl --run reports/smoke/pipeline-c.jsonl --run reports/smoke/pipeline-d.jsonl --output reports/smoke/report.md --summary reports/smoke/metrics-summary.csv
