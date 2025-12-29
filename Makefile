format:
	uvx ruff format ./src ./tests && uvx ruff check --fix ./src ./tests

lint: format
	uvx ruff check ./src ./tests && uvx ty check ./src ./tests

check:
	uvx ruff format --check ./src ./tests && uvx ruff check ./src ./tests && uvx ty check ./src ./tests

test-fixtures:
	./scripts/gen-test-data.sh

test-cli: test-fixtures
	./scripts/test_cli.sh