# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

from enum import Enum


class CLIErrorTypes(Enum):
    pass

class CLIErrorHandler(Exception):
    """CLI error handler"""
    def __init__(self, message: Exception, value: "CLIErrorTypes"):
        self.message: Exception = message
        self.value: "CLIErrorTypes" = value

    def __str__(self):
        pass

class APIErrorTypes(Enum):
    pass

class APIErrorHandler(Exception):
    """API error handler"""
    pass