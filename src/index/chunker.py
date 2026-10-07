# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

from abc import ABC, abstractmethod
from pathlib import Path


class Chunker(ABC):
    """ Chunker class """
    def __init__(self, max_chunk_size: int) -> None:
        self.max_chunk_size: int = max_chunk_size

    @abstractmethod
    def chunk_files(self, files_dict: dict[str, list[Path]]) -> None:
        pass
    pass