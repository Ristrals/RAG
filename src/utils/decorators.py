# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import time
from functools import wraps
from src.lib import Tc


def log_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start_time
        print(f"\n{Tc.cyn}[PERF] {func.__name__} finished in {duration:.4f}s{Tc.clr}\n")
        return result
    return wrapper
