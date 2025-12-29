format:
	black ./aiornot ./tests && ruff --fix ./aiornot ./tests

lint:
	black --check ./aiornot ./tests && ruff ./aiornot ./tests && mypy --install-types --non-interactive ./aiornot ./tests

test-fixtures:
	./scripts/gen-test-data.sh

test-cli: test-fixtures
	./scripts/test_cli.sh