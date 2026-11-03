# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import os

os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"

import fire
from fire.core import FireError
from src.lib import Tc# noqa: E402
from src.interface.cli import RAGCLI  # noqa: E402
from src import (
    OperatorError,
    RetrieverError,
    OracleError,
    EvaluatorError,
    EngineError,
    PathFinderError,
    InterfaceError
)


def main():
    try:
        fire.Fire(RAGCLI)
    except (
        OperatorError,
        RetrieverError,
        OracleError,
        EvaluatorError,
        EngineError,
        PathFinderError,
        InterfaceError,
        FireError,) as e:
        print(f"{Tc.ylw}{e}{Tc.clr}")
        return
    except Exception as e:
        print(f"{Tc.red}[!] Caught Unreferenced Error{Tc.clr}:\n{Tc.ylw}> {e}{Tc.clr}\n")


if __name__ == "__main__":
    main()
