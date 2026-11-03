# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

from enum import Enum
import inspect
from functools import wraps
from pydantic import BaseModel, ValidationError

from src.lib import Tc, ErrType


class CommandName(Enum):
    IND = "Index command (int>250)"
    SRCH = "Search or answer command (str, int>0)"
    EVAL = "Evaluation command(str, str)"
    SRCH_DS = "Search dataset command (str, int>0, str)"
    ANS_DS = "Answer dataset command (str, str)"


def validate_args(model_cls: type[BaseModel], command: CommandName):
    """Decorator that validates arguments against a Pydantic model
    while keeping the original function signature untouched.
    """
    def decorator(func):
        sig = inspect.signature(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            # Separate 'self' from the method arguments so Pydantic doesn't validate it
            arguments = bound.arguments
            self_arg = arguments.pop("self", None)

            try:
                validated = model_cls(**arguments)
            except ValidationError as e:
                raise InterfaceError(ErrType.CRIT, e, command)

            # Re-invoke the original method with 'self' and validated arguments
            call_args = validated.model_dump()
            if self_arg is not None:
                return func(self_arg, **call_args)
            return func(**call_args)

        return wrapper  # <-- Fixed: return wrapper instead of decorator
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
