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

purge:
	rm -rf data/processed
	rm -rf data/output
	rm -rf data/state

purge_lexical:
	rm -rf data/processed/lexical
	rm -rf data/state/rag_state_bm25.json

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

docs:
	uv run python3 src search_dataset "data/datasets/private/UnansweredQuestions/dataset_docs_private.json" 5 "data/output/UnansweredQuestion"
	uv run python3 src evaluate data/output/UnansweredQuestion/dataset_docs_private.json data/datasets/private/AnsweredQuestions/dataset_docs_private.json

code:
	uv run python3 src search_dataset "data/datasets/private/UnansweredQuestions/dataset_code_private.json" 5 "data/output/UnansweredQuestion"
	uv run python3 src evaluate data/output/UnansweredQuestion/dataset_code_private.json data/datasets/private/AnsweredQuestions/dataset_code_private.json