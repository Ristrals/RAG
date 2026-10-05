# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

from pathlib import Path
from src.index import Chunker


class MDChunker(Chunker):
    def chunk_files(self, files_dict) -> None:
        for project, files in files_dict.items():
            project_dir: Path = project
            files_list: list[Path] = files
