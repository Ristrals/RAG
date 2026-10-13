# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import json
from pathlib import Path

# /!\ For local file execution
# from src.index.chunker import Chunker
# from src.index.md_chunker import MDChunker as MdC
# from src.index.py_chunker import PYChunker as PyC

from src.operator import BM25Op, VectorOp
from src.utils import PathFinder
from src.lib import DocSrc
from src.index import Chunker, PYChunker as PyC, MDChunker as MdC
from src.index import Ie, Iet


class Indexer:
    __SUPPORTED_EXT: list[str] = [".py", ".md"]

    def __init__(self, max_chunk_size: int = 1000) -> None:
        self.chunkers: dict[str, Chunker] = {
            "py": PyC(max_chunk_size),
            "md": MdC(max_chunk_size),
        }
        self.operators: dict[str, BM25Op | VectorOp] = {
            "bm25": BM25Op(),
            "vector": VectorOp(),
        }
        self.path_finder = PathFinder()
        self.path_finder.secure_index_directories()
        self.projects: list[Path] = []
        self.py_files: dict[str, list[Path]] = {}
        self.md_files: dict[str, list[Path]] = {}

    def index(self) -> None:
        self.get_files()

        document_sources: list[DocSrc] = []

        self.chunkers["py"].chunk_files(self.py_files)
        self.chunkers["md"].chunk_files(self.md_files)

        for chunker in self.chunkers.values():
            for chunk in chunker.chunks:
                document_sources.append(DocSrc.from_chunk(chunk))

        with open(self.path_finder.processed_dir / "std_index.json", "w", encoding="utf-8") as file:
            file.write(json.dumps([doc.model_dump() for doc in document_sources], indent=4))

        self.operators["bm25"].index(document_sources, self.path_finder.bm25_dir)
        self.operators["vector"].index(document_sources, self.path_finder.vector_dir)

    def get_projects(self) -> None:
        if not self.path_finder.raw_dir.exists():
            raise FileNotFoundError()
        for project in self.path_finder.raw_dir.iterdir():
            if project.is_dir() and not project.name.startswith("."):
                self.projects.append(project)

    def get_files(self) -> None:
        if not self.projects:
            self.get_projects()

        for project in self.projects:
            self.py_files[project.name] = []
            self.md_files[project.name] = []

            for file_path in project.rglob("*"):
                if file_path.is_file() and not file_path.name.startswith("."):
                    ext = file_path.suffix.lower()
                    if ext == ".py":
                        self.py_files[project.name].append(file_path)
                    elif ext == ".md":
                        self.md_files[project.name].append(file_path)
