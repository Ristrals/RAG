# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


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