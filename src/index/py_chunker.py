# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

from pathlib import Path

from src.index import Chunker


class PYChunker(Chunker):
    def __init__(self, max_chunk_size: int) -> None:
        super().__init__(max_chunk_size)

    def chunk_files(self, files_dict) -> None:
        for project, files in files_dict.items():
            project_dir: str = project
            files_list: list[Path] = files