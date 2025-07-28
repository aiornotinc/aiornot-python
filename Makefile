format:
	black ./aiornot ./tests && ruff check --fix ./aiornot ./tests

lint:
	black --check ./aiornot ./tests && ruff check ./aiornot ./tests && mypy --install-types --non-interactive ./aiornot ./tests