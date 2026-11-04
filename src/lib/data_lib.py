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
    mag = "\033[35m"
    pnk = '\033[95m'
    org = '\033[38;2;255;165;0m'
    clr = '\033[0m'


@dataclass
class HeaderNode:
    """Markdown header metadata extracted during parsing.

    Attributes:
        level: Header depth level from 1 to 6.
        title: Header title text.
        start_index: Character offset where the header starts.
        hierarchy: Full hierarchical path for the header.
    """

    level: int
    title: str
    start_index: int
    hierarchy: str


@dataclass
class CodeNode:
    """Python code section metadata extracted from AST.

    Attributes:
        name: Node display name.
        node_type: Node category such as function or method.
        start_index: Character offset where the section starts.
        end_index: Character offset where the section ends.
        hierarchy: Hierarchical label of the section.
    """

    name: str
    node_type: str  # "class", "function", "method", "preamble"
    start_index: int
    end_index: int
    hierarchy: str


@dataclass
class Chunk:
    """Chunked text segment with source location metadata.

    Attributes:
        content: Chunk text content.
        start_index: Start offset in the source file.
        end_index: End offset in the source file.
        hierarchy: Section hierarchy associated with the chunk.
        file_path: Source file path.
        project: Source project identifier.
    """

    content: str
    start_index: int
    end_index: int
    hierarchy: str
    file_path: Path
    project: str


class ResearchType(Enum):
    """Supported retrieval modes for indexing and search."""

    LEXICAL = "lexical"
    VECTOR = "vector"
    HYBRID = "hybrid"


class ErrorType(Enum):
    """Supported error severity levels."""

    WRN = "WARNING"
    CRIT = "CRITICAL"


class StopWords:
    """Default stop-word list used for lexical preprocessing."""

    STOP_WORDS = {
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
        "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
        "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
        "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
        "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
        "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
        "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
        "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
        "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
        "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
        "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
        "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than",
        "that", "that's", "the", "their", "theirs", "them", "themselves", "then",
        "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've",
        "this", "those", "through", "to", "too", "under", "until", "up", "very",
        "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't",
        "what", "what's", "when", "when's", "where", "where's", "which", "while",
        "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't",
        "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself",
        "yourselves", "vllm", "model"
    }
