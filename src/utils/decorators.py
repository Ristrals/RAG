# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

"""Shared decorators for runtime instrumentation and helper behavior."""

import time
from collections.abc import Callable
from typing import ParamSpec, TypeVar
from functools import wraps
from src.lib import Tc


P = ParamSpec("P")
R = TypeVar("R")


# Time log
def log_execution_time(func: Callable[P, R]) -> Callable[P, R]:
    """Measure and print execution time for a wrapped callable.

    Args:
        func: Callable to execute with timing instrumentation.

    Returns:
        Wrapped callable preserving the original signature.
    """

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start_time
        print(f"\n{Tc.cyn}[PERF] {func.__name__} finished in {duration:.4f}s{Tc.clr}\n")
        return result
    return wrapper
