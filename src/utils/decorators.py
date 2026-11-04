# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import time
from collections.abc import Callable
from typing import ParamSpec, TypeVar
from functools import wraps
from src.lib import Tc


P = ParamSpec("P")
R = TypeVar("R")


# Time log
def log_execution_time(func: Callable[P, R]) -> Callable[P, R]:

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start_time
        print(f"\n{Tc.cyn}[PERF] {func.__name__} finished in {duration:.4f}s{Tc.clr}\n")
        return result
    return wrapper
