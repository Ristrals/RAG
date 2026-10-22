# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import re
import bm25s
import json
from pathlib import Path

from src.lib import DocSrc, Tc
from src.utils import PathFinder
from src.utils.decorators import log_execution_time


class BM25Operator:
    def __init__(self, path_finder: PathFinder, docsrc_store: dict[str, DocSrc]) -> None:
        self.path_finder = path_finder
        self.retriever: bm25s.BM25 | None = None
        self.doc_ids: list[str] = []
        self.docsrc_store: dict[str, DocSrc] = docsrc_store
        self._dirty: bool = False

    def tokenize(self, text: str) -> list[str]:
        return re.findall(r"\w+", text.lower())

    @log_execution_time
    def index(self, target_docs: dict[str, DocSrc] | None = None) -> None:
        # If no new documents AND no deletions occurred, skip entirely!
        is_empty_target = target_docs is not None and len(target_docs) == 0
        if is_empty_target and not self._dirty:
            return

        print(f"{Tc.org}[BM25S]{Tc.clr} Lexical indexing . . .")

        # bm25s always indexes the complete active docsrc_store for accurate IDF
        docs_to_index = self.docsrc_store
        if not docs_to_index:
            self.doc_ids = []
            self.retriever = None
            if self.path_finder.link_path.exists():
                self.path_finder.link_path.unlink()
            self._dirty = False
            return

        self.doc_ids = list(docs_to_index.keys())
        corpus_texts = [self.tokenize(doc.text) for doc in docs_to_index.values()]

        self.retriever = bm25s.BM25()
        assert isinstance(self.retriever, bm25s.BM25)
        self.retriever.index(corpus_texts)

        self.path_finder.bm25_dir.mkdir(parents=True, exist_ok=True)
        self.retriever.save(str(self.path_finder.bm25_dir))

        with open(self.path_finder.link_path, "w", encoding="utf-8") as file:
            json.dump(self.doc_ids, file)

        self._dirty = False

    def load(self) -> None:
        self.retriever = bm25s.BM25.load(str(self.path_finder.bm25_dir))
        with open(self.path_finder.link_path, "r", encoding="utf-8") as file:
            self.doc_ids = json.load(file)

    def search(self, query: str, k: int = 10) -> list[tuple[str, float]]:
        """Scores query against BM25 index and maps matrix indices back to fingerprints."""

        if self.retriever is None:
            if self.path_finder.bm25_dir is None:
                raise RuntimeError("BM25 index is not loaded and no index directory referenced.")
            self.load()

        query_tokens = self.tokenize(query)
        if not query_tokens:
            return []

        assert isinstance(self.retriever, bm25s.BM25)
        results, scores = self.retriever.retrieve([query_tokens], k=min(k, len(self.doc_ids)))

        found = []
        for doc_idx, score in zip(results[0], scores[0]):
            fingerprint = self.doc_ids[doc_idx]
            found.append((fingerprint, float(score)))

        return found

    def delete(self, file_paths: Path | list[Path] | set[Path]) -> None:
        """Removes all chunks associated with file_path from the shared docsrc_store and re-indexes."""

        if isinstance(file_paths, Path):
            paths_to_remove = {file_paths}
        else:
            paths_to_remove = {Path(p) for p in file_paths}

        remaining_docs = {
            doc_id: doc for doc_id, doc in self.docsrc_store.items()
            if Path(doc.file_path) not in paths_to_remove
        }

        self.docsrc_store.clear()
        self.docsrc_store.update(remaining_docs)
        self._dirty = True