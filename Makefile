.PHONY: format lint publish

format:
	uvx black ./aiornot ./tests && uvx ruff check --fix ./aiornot ./tests

lint:
	uvx black --check ./aiornot ./tests && uvx ruff check ./aiornot ./tests && uvx --with aiofiles --with click --with httpx --with "mcp>=1.0.0" --with pydantic --with pytest --with types-aiofiles --with types-jsonschema --with types-pexpect --with types-Pygments --with types-PyYAML mypy --install-types --non-interactive ./aiornot ./tests

publish:
	@test -n "$$PYPI_API_TOKEN" || (echo "PYPI_API_TOKEN is required" && exit 1)
	uv build
	uv publish --token "$$PYPI_API_TOKEN"
