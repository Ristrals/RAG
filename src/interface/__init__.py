# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

"""Public exports for CLI/API argument validation and interface errors."""

from src.interface.interface_error import CommandName, validate_args, InterfaceError


__all__ = [
    "CommandName", "validate_args", "InterfaceError",
]
