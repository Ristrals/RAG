# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import functools
from enum import Enum
from collections.abc import Callable
from typing import ParamSpec, TypeVar

from src.lib import Tc
from src.lib import ErrType


class OpErrType(Enum):
    """Operation phases used for operator error context."""

    IND = "indexing"
    SRCH = "search"
    DEL = "deletion"


class OpType(Enum):
    """Supported operator backends."""

    BM25 = "BM25"
    VCTR = "Vector"


P = ParamSpec("P")
R = TypeVar("R")


def operator_error_handler(
    op: OpType,
    src: OpErrType,
    err_type: ErrType = ErrType.CRIT
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Wrap operator methods and re-raise failures as OperatorError.

    Args:
        op: Operator backend where the error originates.
        src: Operation phase that failed.
        err_type: Error severity used for formatting.

    Returns:
        Decorator preserving wrapped callable signature.
    """
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
    """Error raised by operator backends.

    Attributes:
        err_type: Severity level of the error.
        err: Underlying raised exception.
        op: Operator backend that failed.
        err_src: Operation phase where the failure occurred.
    """

    def __init__(self, err_type: ErrType, err: Exception, op: OpType, err_src: OpErrType):
        """Initialize an operator error wrapper.

        Args:
            err_type: Severity for error rendering.
            err: Underlying exception.
            op: Operator backend identifier.
            err_src: Failed operation phase.

        """
        self.err_type: ErrType = err_type
        self.err: Exception = err
        self.op: OpType = op
        self.err_src: OpErrType = err_src

    def __str__(self) -> str:
        """Return a formatted and colorized error message.

        Returns:
            Human-readable operator error details.
        """
        msg: str = ""
        match self.err_type:
            case ErrType.CRIT: msg += f"{Tc.red}[!] Caught Critical {self.op.value}OperatorError{Tc.clr}:\n"
            case ErrType.WRN: msg += f"{Tc.ylw}[!] Caught {self.op.value}OperatorError Warning{Tc.clr}:\n"
        msg += f"{Tc.ylw}> An error has occurred during {self.err_src.value}:\n{Tc.clr}"
        msg += f"{Tc.ylw}> {self.err}\n{Tc.clr}"
        return msg
