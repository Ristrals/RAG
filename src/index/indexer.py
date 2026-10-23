# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import json
from pathlib import Path

# /!\ For local file execution
# from src.index.chunker import Chunker
# from src.index.md_chunker import MDChunker as MdC
# from src.index.py_chunker import PYChunker as PyC

from src.operators import BM25Op, VectorOp
from src.utils import PathFinder
from src.lib import DocSrc, RsrchType
from src.index import Chunker, PYChunker as PyC, MDChunker as MdC, Sync
from src.index import Ie, Iet


class Indexer:
    __SUPPORTED_EXT: list[str] = [".py", ".md", ".txt"]

    def __init__(self, max_chunk_size: int = 1000, mode: RsrchType = RsrchType.LEXICAL) -> None:
        self.chunkers: dict[str, Chunker] = {
            "py": PyC(max_chunk_size),
            "md": MdC(max_chunk_size),
        }
        self.mode: RsrchType = mode
        self.path_finder = PathFinder()
        self.path_finder.secure_index_directories()
        self.docsrc_store: dict[str, DocSrc] = {}
        self._load_doc_store()
        self.operators: dict[str, BM25Op | VectorOp] = {
            "bm25": BM25Op(self.path_finder, self.docsrc_store),
            "vector": VectorOp(self.path_finder, self.docsrc_store),
        }
        self.sync_bm25: Sync = Sync(
            self.path_finder,
            self.docsrc_store,
            self.path_finder.rag_state_bm25_path,
            self.operators["bm25"],
        )
        self.sync_vector: Sync = Sync(
            self.path_finder,
            self.docsrc_store,
            self.path_finder.rag_state_vector_path,
            self.operators["vector"],
        )
        self.projects: list[Path] = []
        self.py_files: dict[str, list[Path]] = {}
        self.md_files: dict[str, list[Path]] = {}

    def index(self) -> None:
        if self.mode == RsrchType.LEXICAL or self.mode == RsrchType.HYBRID:
            self.sync_bm25.check_projects()
            self._execute_pipeline(self.sync_bm25, self.operators["bm25"])

        if self.mode == RsrchType.VECTOR or self.mode == RsrchType.HYBRID:
            self.sync_vector.check_projects()
            self._execute_pipeline(self.sync_vector, self.operators["vector"])

    def _execute_pipeline(self, synchronizer: Sync, operator: BM25Op | VectorOp) -> None:
        if any(files for files in synchronizer.py_files_to_process.values()):
            self.chunkers["py"].chunk_files(synchronizer.py_files_to_process)

        if any(files for files in synchronizer.md_files_to_process.values()):
            self.chunkers["md"].chunk_files(synchronizer.md_files_to_process)

        new_docs: dict[str, DocSrc] = {}
        for chunker in self.chunkers.values():
            for chunk in chunker.chunks:
                doc = DocSrc.from_chunk(chunk)
                self.docsrc_store[doc.id] = doc
                new_docs[doc.id] = doc
            chunker.chunks.clear()  # reset chunker buffer for the next pass

        with open(self.path_finder.docsrc_path, "w", encoding="utf-8") as file:
            file.write(json.dumps([doc.model_dump() for doc in self.docsrc_store.values()], indent=4))

        synchronizer.export_rag_state()
        operator.index(new_docs)

    def _load_doc_store(self) -> None:
        if self.path_finder.docsrc_path.exists():
            with open(self.path_finder.docsrc_path, "r", encoding="utf-8") as f:
                raw_docs: list[dict] = json.load(f)
            self.docsrc_store = {
                item["id"]: DocSrc.model_validate(item)
                for item in raw_docs
            }
