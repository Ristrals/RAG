# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

from src.lib import Tc, ErrType


class PathFinderError(Exception):
    def __init__(self, err_type: ErrType, err: Exception) -> None:
        self.err_type: ErrType = err_type
        self.err: Exception = err

    def __str__(self) -> str:
        msg = ""
        match self.err_type:
            case ErrType.CRIT: msg += f"{Tc.red}[!] Caught Critical PathFinderError{Tc.clr}:\n"
            case ErrType.WRN: msg += f"{Tc.ylw}[!] Caught PathFinderError Warning{Tc.clr}:\n"
        msg += f"{Tc.ylw}> {self.err}{Tc.clr}\n"
        return msg
