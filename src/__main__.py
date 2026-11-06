# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import logging
import fire
from fire.core import FireError
from src.lib import Tc
from src.interface.cli import RAGCLI
from src import (
    OperatorError,
    RetrieverError,
    OracleError,
    EvaluatorError,
    EngineError,
    PathFinderError,
    InterfaceError
)
# Silences transformers warnings
logging.getLogger("transformers").setLevel(logging.ERROR)


def main() -> None:
    """Run the Fire CLI and handle known application exceptions."""

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
        FireError
    ) as e:
        print(f"{Tc.ylw}{e}{Tc.clr}")
        return
    except Exception as e:
        print(f"{Tc.red}[!] Caught Unreferenced Error{Tc.clr}:\n{Tc.ylw}> {e}{Tc.clr}\n")


if __name__ == "__main__":
    main()
