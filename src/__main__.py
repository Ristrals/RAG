# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import os

os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"

import fire  # noqa: E402
from src.interface.cli import RAGCLI  # noqa: E402


def main():
    fire.Fire(RAGCLI)


if __name__ == "__main__":
    main()
