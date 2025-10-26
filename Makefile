.PHONY: setup lint lint-fix test test-quick

setup:
	uv sync --dev --extra cpu

lint:
	uvx ruff check .

lint-fix:
	uvx ruff check . --fix

test:
	PYTHONUTF8=1 NANOCHAT_BASE_DIR=$(PWD)/.cache/nanochat PYTHONPATH=$(PWD) uv run pytest -q

test-quick:
	PYTHONUTF8=1 NANOCHAT_BASE_DIR=$(PWD)/.cache/nanochat PYTHONPATH=$(PWD) uv run pytest -q -k correctness -q

