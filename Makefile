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
	uv run python scripts/run_benchmark.py --config configs/experiments/smoke.yml --model mock --limit 30 --output reports/smoke
