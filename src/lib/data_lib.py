# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

class TextColors:
    """ANSI color codes for terminal output formatting.

    Attributes:
        red: Red terminal color code.
        blu: Blue terminal color code.
        grn: Green terminal color code.
        ylw: Yellow terminal color code.
        cyn: Cyan terminal color code.
        pnk: Pink terminal color code.
        org: Orange terminal color code.
        clr: Terminal color reset code.
    """
    red = '\033[91m'
    blu = '\033[94m'
    grn = '\033[92m'
    ylw = '\033[93m'
    cyn = '\033[36m'
    pnk = '\033[95m'
    org = '\033[38;2;255;165;0m'
    clr = '\033[0m'


@dataclass
class HeaderNode:
    level: int
    title: str
    start_index: int
    hierarchy: str


@dataclass
class CodeNode:
    name: str
    node_type: str  # "class", "function", "method", "preamble"
    start_index: int
    end_index: int
    hierarchy: str


@dataclass
class Chunk:
    content: str
    start_index: int
    end_index: int
    hierarchy: str
    file_path: Path
    project: str

class ResearchType(Enum):
    LEXICAL = "lexical"
    VECTOR = "vector"
    HYBRID = "hybrid"