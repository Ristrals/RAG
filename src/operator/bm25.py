# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import re
import bm25s
import json
from pathlib import Path

from src.lib import DocSrc


class BM25Operator:
    def __init__(self) -> None:
        self.retriever: bm25s.BM25 | None = None
        self.doc_ids: list[str] = []

    def tokenize(self, text: str) -> list[str]:
        return re.findall(r"\w+", text.lower())

    def index(self, documents: list[DocSrc], output_dir: Path) -> None:
        if not documents:
            return

        self.doc_ids = [doc.id for doc in documents]
        corpus_texts = [self.tokenize(doc.text) for doc in documents]

        self.retriever = bm25s.BM25()
        assert isinstance(self.retriever, bm25s.BM25)
        self.retriever.index(corpus_texts)

        output_dir.mkdir(parents=True, exist_ok=True)
        self.retriever.save(str(output_dir))

        with open(output_dir / "std_bm25_link.json", "w", encoding="utf-8") as file:
            json.dump(self.doc_ids, file)

    def load(self, index_dir: Path) -> None:
        self.retriever = bm25s.BM25.load(str(index_dir))
        with open(index_dir / "std_bm25_link.json", "r", encoding="utf-8") as file:
            self.doc_ids = json.load(file)

    def search(self, query: str, index_dir: Path | None, k: int = 10) -> list[tuple[str, float]]:
        """Scores query against BM25 index and maps matrix indices back to fingerprints."""

        if self.retriever is None:
            if index_dir is None:
                raise RuntimeError("BM25 index is not loaded and no index directory referenced.")
            self.load(index_dir)

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
