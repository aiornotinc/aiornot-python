.PHONY: install format lint check test test-cov test-fixtures test-cli clean

install:
	uv sync --dev

format:
	uvx ruff format ./src ./tests && uvx ruff check --fix ./src ./tests

lint: format
	uvx ruff check ./src ./tests && uvx ty check ./src ./tests

check:
	uvx ruff format --check ./src ./tests && uvx ruff check ./src ./tests && uvx ty check ./src ./tests

test:
	uv run pytest

test-cov:
	uv run coverage run -m pytest && uv run coverage report -m

test-fixtures:
	./scripts/gen-test-data.sh

test-cli: test-fixtures
	./scripts/test_cli.sh

clean:
	rm -rf dist/ *.egg-info/ .pytest_cache/ .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
