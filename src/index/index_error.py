# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

from enum import Enum


class IndexerErrorTypes(Enum):
    DIR_NOT_FOUND = "raw directory not found"

    @property
    def error_str(self) -> str:
        return self.value

class IndexerError(Exception):
    """Index error handler"""
    def __init__(self, err_type: "IndexerErrorTypes", message: Exception):
        self.err_type: "IndexerErrorTypes" = err_type
        self.message: Exception = message

    def __str__(self):
        pass

class APIErrorTypes(Enum):
    pass

class APIErrorHandler(Exception):
    """API error handler"""
    pass