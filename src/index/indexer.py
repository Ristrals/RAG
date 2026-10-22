# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import json
from pathlib import Path

# /!\ For local file execution
# from src.index.chunker import Chunker
# from src.index.md_chunker import MDChunker as MdC
# from src.index.py_chunker import PYChunker as PyC

from src.operators import BM25Op, VectorOp
from src.utils import PathFinder
from src.lib import DocSrc
from src.index import Chunker, PYChunker as PyC, MDChunker as MdC, Sync
from src.index import Ie, Iet


class Indexer:
    __SUPPORTED_EXT: list[str] = [".py", ".md", ".txt"]

    def __init__(self, max_chunk_size: int = 1000) -> None:
        self.chunkers: dict[str, Chunker] = {
            "py": PyC(max_chunk_size),
            "md": MdC(max_chunk_size),
        }
        self.path_finder = PathFinder()
        self.path_finder.secure_index_directories()
        self.docsrc_store: dict[str, DocSrc] = {}
        self._load_doc_store()
        self.operators: dict[str, BM25Op | VectorOp] = {
            "bm25": BM25Op(self.path_finder, self.docsrc_store),
            "vector": VectorOp(self.path_finder, self.docsrc_store),
        }
        self.synchronizer: Sync = Sync(
            self.path_finder,
            self.docsrc_store,
            self.operators["bm25"],
            self.operators["vector"],
        )
        self.projects: list[Path] = []
        self.py_files: dict[str, list[Path]] = {}
        self.md_files: dict[str, list[Path]] = {}

    def index(self) -> None:
        self.synchronizer.check_projects()

        self.chunkers["py"].chunk_files(self.synchronizer.py_files_to_process)
        self.chunkers["md"].chunk_files(self.synchronizer.md_files_to_process)

        new_docsrc_store: dict[str, DocSrc] = {}

        for chunker in self.chunkers.values():
            for chunk in chunker.chunks:
                doc = DocSrc.from_chunk(chunk)
                self.docsrc_store[doc.id] = doc
                new_docsrc_store[doc.id] = doc

        with open(self.path_finder.docsrc_path, "w", encoding="utf-8") as file:
            file.write(json.dumps([doc.model_dump() for doc in self.docsrc_store.values()], indent=4))

        self.synchronizer.export_rag_state()

        self.operators["bm25"].index(new_docsrc_store)
        self.operators["vector"].index(new_docsrc_store)

    def _load_doc_store(self) -> None:
        if self.path_finder.docsrc_path.exists():
            with open(self.path_finder.docsrc_path, "r", encoding="utf-8") as f:
                raw_docs: list[dict] = json.load(f)
            self.docsrc_store = {
                item["id"]: DocSrc.model_validate(item)
                for item in raw_docs
            }
