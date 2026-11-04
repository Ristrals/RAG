# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

from enum import Enum
import inspect
from functools import wraps
from pydantic import BaseModel, ValidationError
from collections.abc import Callable
from typing import ParamSpec, TypeVar

from src.lib import Tc, ErrType


class CommandName(Enum):
    IND = "Index command (int>250)"
    SRCH = "Search or answer command (str, int>0)"
    EVAL = "Evaluation command(str, str)"
    SRCH_DS = "Search dataset command (str, int>0, str)"
    ANS_DS = "Answer dataset command (str, str)"


P = ParamSpec("P")
R = TypeVar("R")


def validate_args(
    model_cls: type[BaseModel],
    command: CommandName
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator that validates arguments against a Pydantic model
    while keeping the original function signature untouched.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        sig = inspect.signature(func)

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            arguments = bound.arguments
            self_arg = arguments.pop("self", None)

            try:
                validated = model_cls(**arguments)
            except ValidationError as e:
                raise InterfaceError(ErrType.CRIT, e, command)

            call_args = validated.model_dump()
            if self_arg is not None:
                return func(self_arg, **call_args)

            return func(**call_args)  # type: ignore[call-arg]
        return wrapper
    return decorator


class InterfaceError(Exception):
    def __init__(self, err_type: ErrType, err: Exception, command: CommandName) -> None:
        self.err_type: ErrType = err_type
        self.err: Exception = err
        self.command: CommandName = command

    def __str__(self) -> str:
        msg = ""
        match self.err_type:
            case ErrType.CRIT: msg += f"{Tc.red}[!] Caught Critical InterfaceError{Tc.clr}:\n"
            case ErrType.WRN: msg += f"{Tc.ylw}[!] Caught InterfaceError Warning{Tc.clr}:\n"
        msg += f"{Tc.ylw}> Invalid argument for {self.command.value}:\n"
        msg += f"> {self.err}{Tc.clr}\n"
        return msg
