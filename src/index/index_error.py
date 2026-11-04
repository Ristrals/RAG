# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

from enum import Enum
from pathlib import Path
from pydantic import ValidationError
from json import JSONDecodeError

from src.lib import ErrType, Tc


class ChunkerType(Enum):
    """Supported chunker categories used in error reporting."""

    PY = "Python"
    MD = "Mark Down"
    TXT = "Text"


class ChunkerError(Exception):
    """Error raised when chunking operations fail or degrade.

    Attributes:
        err_type: Severity level of the error.
        err: Underlying exception instance.
        chunker: Chunker type that raised the error.
        file_path: Optional file path associated with the error.
    """

    def __init__(self, err_type: ErrType, err: Exception, chunker: ChunkerType, file_path: Path | None = None) -> None:
        """Initialize a chunker error wrapper.

        Args:
            err_type: Severity for the error message.
            err: Original exception to wrap.
            chunker: Chunker category where the error occurred.
            file_path: Optional path to the failing file.

        """
        self.err_type: ErrType = err_type
        self.err: Exception = err
        self.chunker: ChunkerType = chunker
        self.file_path: Path | None = file_path

    def __str__(self) -> str:
        """Return a formatted and colorized error message.

        Returns:
            Human-readable error details.
        """
        msg = ""
        match self.err_type:
            case ErrType.CRIT: msg += f"{Tc.red}[!] Caught Critical {self.chunker.value} ChunkerError{Tc.clr}:\n"
            case ErrType.WRN: msg += f"{Tc.ylw}[!] Caught {self.chunker.value} ChunkerError Warning{Tc.clr}:\n"
        if isinstance(self.err, (ValidationError, JSONDecodeError)):
            msg += f"{Tc.ylw}Invalid json schema:\n{Tc.clr}"
        if isinstance(self.err, SyntaxError):
            msg += (
                f"{Tc.ylw}> SyntaxError in '{str(self.file_path)}'\n"
                f"> at line {self.err.lineno}: {self.err.text.strip() if self.err.text else self.err.msg}\n"
                f"> Falling back to raw text chunking.\n{Tc.clr}")
            return msg
        msg += f"{Tc.ylw}> {self.err}{Tc.clr}\n"
        return msg


class IndexerError(Exception):
    """Error raised for indexer orchestration issues.

    Attributes:
        err_type: Severity level of the error.
        err: Underlying exception instance.
    """

    def __init__(self, err_type: ErrType, err: Exception) -> None:
        """Initialize an indexer error wrapper.

        Args:
            err_type: Severity for the error message.
            err: Original exception to wrap.

        """
        self.err_type: ErrType = err_type
        self.err: Exception = err

    def __str__(self) -> str:
        """Return a formatted and colorized error message.

        Returns:
            Human-readable error details.
        """
        msg = ""
        match self.err_type:
            case ErrType.CRIT: msg += f"{Tc.red}[!] Caught Critical IndexerError{Tc.clr}:\n"
            case ErrType.WRN: msg += f"{Tc.ylw}[!] Caught IndexerError Warning{Tc.clr}:\n"
        msg += f"{Tc.ylw}> {self.err}{Tc.clr}\n"
        return msg
