# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

from src.lib import Tc, ErrType


class PathFinderError(Exception):
    """Error raised by path and directory management utilities.

    Attributes:
        err_type: Severity level for error reporting.
        err: Underlying exception instance.
    """

    def __init__(self, err_type: ErrType, err: Exception) -> None:
        """Initialize a path-finder error wrapper.

        Args:
            err_type: Severity for message formatting.
            err: Underlying exception.

        """
        self.err_type: ErrType = err_type
        self.err: Exception = err

    def __str__(self) -> str:
        """Return a formatted and colorized error message.

        Returns:
            Human-readable path-finder error details.
        """
        msg = ""
        match self.err_type:
            case ErrType.CRIT: msg += f"{Tc.red}[!] Caught Critical PathFinderError{Tc.clr}:\n"
            case ErrType.WRN: msg += f"{Tc.ylw}[!] Caught PathFinderError Warning{Tc.clr}:\n"
        msg += f"{Tc.ylw}> {self.err}{Tc.clr}\n"
        return msg
