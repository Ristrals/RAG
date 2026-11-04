# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import functools
from enum import Enum
from collections.abc import Callable
from typing import ParamSpec, TypeVar

from src.lib import Tc
from src.lib import ErrType


class OpErrType(Enum):
    IND = "indexing"
    SRCH = "search"
    DEL = "deletion"


class OpType(Enum):
    BM25 = "BM25"
    VCTR = "Vector"


P = ParamSpec("P")
R = TypeVar("R")


def operator_error_handler(
    op: OpType,
    src: OpErrType,
    err_type: ErrType = ErrType.CRIT
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator to catch and handle known RAG application and unexpected errors."""
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                raise OperatorError(err_type, e, op, src)
        return wrapper
    return decorator


class OperatorError(Exception):
    def __init__(self, err_type: ErrType, err: Exception, op: OpType, err_src: OpErrType):
        self.err_type: ErrType = err_type
        self.err: Exception = err
        self.op: OpType = op
        self.err_src: OpErrType = err_src

    def __str__(self) -> str:
        msg: str = ""
        match self.err_type:
            case ErrType.CRIT: msg += f"{Tc.red}[!] Caught Critical {self.op.value}OperatorError{Tc.clr}:\n"
            case ErrType.WRN: msg += f"{Tc.ylw}[!] Caught {self.op.value}OperatorError Warning{Tc.clr}:\n"
        msg += f"{Tc.ylw}> An error has occurred during {self.err_src.value}:\n{Tc.clr}"
        msg += f"{Tc.ylw}> {self.err}\n{Tc.clr}"
        return msg
