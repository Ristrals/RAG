# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois
from src.lib import Tc, ErrType
from pydantic import ValidationError
from json import JSONDecodeError


class RetrieverError(Exception):
    def __init__(self, err_type: ErrType, err: Exception) -> None:
        self.err_type: ErrType = err_type
        self.err: Exception = err

    def __str__(self) -> str:
        msg = ""
        match self.err_type:
            case ErrType.CRIT: msg += f"{Tc.red}[!] Caught Critical RetrieverError{Tc.clr}:\n"
            case ErrType.WRN: msg += f"{Tc.ylw}[!] Caught RetrieverError Warning{Tc.clr}:\n"
        if isinstance(self.err, (ValidationError, JSONDecodeError)):
            msg += f"{Tc.ylw}Invalid json schema:\n{Tc.clr}"
        msg += f"{Tc.ylw}> {self.err}{Tc.clr}\n"
        return msg


class OracleError(Exception):
    def __init__(self, err_type: ErrType, err: Exception) -> None:
        self.err_type: ErrType = err_type
        self.err: Exception = err

    def __str__(self) -> str:
        msg = ""
        match self.err_type:
            case ErrType.CRIT: msg += f"{Tc.red}[!] Caught Critical OracleError{Tc.clr}:\n"
            case ErrType.WRN: msg += f"{Tc.ylw}[!] Caught OracleError Warning{Tc.clr}:\n"
        if isinstance(self.err, (ValidationError, JSONDecodeError)):
            msg += f"{Tc.ylw}> Student Search Result Invalid json schema:\n{Tc.clr}"
        msg += f"{Tc.ylw}> {self.err}{Tc.clr}\n"
        return msg


class EvaluatorError(Exception):
    def __init__(self, err_type: ErrType, err: Exception, specific: int) -> None:
        self.err_type: ErrType = err_type
        self.err: Exception = err
        self.specific: int = specific

    def __str__(self) -> str:
        msg = ""
        match self.err_type:
            case ErrType.CRIT: msg += f"{Tc.red}[!] Caught Critical EvaluatorError{Tc.clr}:\n"
            case ErrType.WRN: msg += f"{Tc.ylw}[!] Caught EvaluatorError Warning{Tc.clr}:\n"
        if isinstance(self.err, (ValidationError, JSONDecodeError)):
            match self.specific:
                case 0: msg += f"{Tc.ylw}> Student Search Results "
                case 1: msg += f"{Tc.ylw}> Ground Truth "
            msg += f"invalid json schema:\n{Tc.clr}"
        msg += f"{Tc.ylw}> {self.err}{Tc.clr}\n"
        return msg

class EngineError(Exception):
    def __init__(self, err_type: ErrType, err: Exception) -> None:
        self.err_type: ErrType = err_type
        self.err: Exception = err

    def __str__(self) -> str:
        msg = ""
        match self.err_type:
            case ErrType.CRIT: msg += f"{Tc.red}[!] Caught Critical EngineError{Tc.clr}:\n"
            case ErrType.WRN: msg += f"{Tc.ylw}[!] Caught EngineError Warning{Tc.clr}:\n"
        msg += f"{Tc.ylw}> {self.err}{Tc.clr}\n"
        return msg
