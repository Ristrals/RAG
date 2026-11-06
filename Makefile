PC = python3

run:
	uv run $(PC) -m src index 2000
	uv run $(PC) -m src answer "What is vLLM?" 5

debug:
	uv run $(PC) -m pdb -m src index 2000
	uv run $(PC) -m pdb -m src answer "What is vLLM?" 5

install:
	uv sync

clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +

purge:
	rm -rf data/processed
	rm -rf data/output
	rm -rf data/state

fclean: clean purge
	rm -rf .venv
	rm -rf .cache/uv
	uv cache clean

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
