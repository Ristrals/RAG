PC = python3

run:
	uv run $(PC) -m src

index:
	uv run $(PC) -m src index "alpha"

debug:
	uv run $(PC) -m pdb -m src

install:
	uv venv

sync:
	uv sync

clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +

fclean: clean
	rm -rf .venv
	rm -rf .cache/uv uv cache clean

lint:
	flake8
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

mp:
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

f8:
	flake8

lint-strict:
	flake8
	mypy . --strict