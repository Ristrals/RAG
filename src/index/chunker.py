# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

from abc import ABC, abstractmethod
from pathlib import Path


class Chunker(ABC):
    """ Chunker class """

    @abstractmethod
    def chunk_files(self, files_dict: dict[Path, list[Path]]) -> None:
        pass
    pass