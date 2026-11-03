# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

from enum import Enum
from pathlib import Path
from pydantic import ValidationError
from json import JSONDecodeError

from src.lib import ErrType, Tc


class ChunkerType(Enum):
    PY = "Python"
    MD = "Mark Down"
    TXT = "Text"

class ChunkerError(Exception):
    def __init__(self, err_type: ErrType, err: Exception, chunker: ChunkerType, file_path: Path | None = None) -> None:
        self.err_type: ErrType = err_type
        self.err: Exception = err
        self.chunker: ChunkerType = chunker
        self.file_path: Path | None = file_path

    def __str__(self) -> str:
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
    def __init__(self, err_type: ErrType, err: Exception) -> None:
        self.err_type: ErrType = err_type
        self.err: Exception = err

    def __str__(self) -> str:
        msg = ""
        match self.err_type:
            case ErrType.CRIT: msg += f"{Tc.red}[!] Caught Critical IndexerError{Tc.clr}:\n"
            case ErrType.WRN: msg += f"{Tc.ylw}[!] Caught IndexerError Warning{Tc.clr}:\n"
        msg += f"{Tc.ylw}> {self.err}{Tc.clr}\n"
        return msg