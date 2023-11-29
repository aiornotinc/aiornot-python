format:
	black ./aiornot ./tests && ruff --fix ./aiornot ./tests

lint:
	black --check ./aiornot ./tests && ruff ./aiornot ./tests && mypy --install-types --non-interactive ./aiornot ./tests