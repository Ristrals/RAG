# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

from pathlib import Path

from src.index.chunker import Chunker
from src.index.md_chunker import MDChunker as MdC
from src.index.py_chunker import PYChunker as PyC

# from src.index import Chunker, PYChunker as PyC, MDChunker as MdC
# from src.index import Ie, Iet


class Indexer:
    __SUPPORTED_EXT: list[str] = [".py", ".md"]

    def __init__(self, max_chunk_size: int = 1000) -> None:
        self.chunkers: dict[str, Chunker] = {
            "py": PyC(max_chunk_size),
            "md": MdC(max_chunk_size),
        }
        self.raw_dir: Path = Path("data/raw")
        self.projects: list[Path] = []
        self.py_files: dict[str, list[Path]] = {}
        self.md_files: dict[str, list[Path]] = {}

    def index(self) -> None:
        self.get_files()
        self.chunkers["py"].chunk_files(self.py_files)
        self.chunkers["md"].chunk_files(self.md_files)


    def get_projects(self) -> None:
        if not self.raw_dir.exists():
            raise FileNotFoundError()
        for project in self.raw_dir.iterdir():
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