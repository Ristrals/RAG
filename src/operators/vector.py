# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import chromadb
from typing import Any
from pathlib import Path
from chromadb.utils import embedding_functions

from src.lib import DocSrc


class VectorOperator:
    _BATCH_SIZE = 5000

    def __init__(
            self,
            collection_name: str = "ragtm_chunks",
            embedding_model: str = "all-MiniLM-L6-v2",
    ) -> None:

        self.output_dir: Path = Path()
        self.collection_name = collection_name
        self.embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model
        )
        self._client: Any | None = None
        self._collection: chromadb.Collection | None = None

    def _get_collection(self, index_dir: Path | None = None) -> chromadb.Collection:
        """Load or initialize ChromaDB persistent client and collection."""
        target_dir = index_dir if index_dir is not None else self.output_dir

        if self._collection is None or self._client is None or target_dir != self.output_dir:
            self.output_dir = target_dir
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(path=str(self.output_dir))
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_func,
                metadata={"hnsw:space": "cosine"},
            )

        assert self._collection is not None
        return self._collection

    def index(self, documents: list[DocSrc], output_dir: Path) -> None:
        if not documents:
            return

        collection = self._get_collection(output_dir)

        ids = [doc.id for doc in documents]
        texts = [doc.text for doc in documents]
        metadatas = [
            {
                "project": doc.project,
                "file_path": doc.file_path,
                "hierarchy": doc.hierarchy,
                "content_hash": doc.content_hash,
                "first_character_index": doc.first_character_index,
                "last_character_index": doc.last_character_index,
            }
            for doc in documents
        ]

        total_chunks = len(ids)
        for i in range(0, total_chunks, self._BATCH_SIZE):
            batch_ids = ids[i: i + self._BATCH_SIZE]
            batch_documents = texts[i: i + self._BATCH_SIZE]
            batch_metadatas = metadatas[i: i + self._BATCH_SIZE]

            collection.upsert(
                ids=batch_ids,
                documents=batch_documents,
                metadatas=batch_metadatas,
            )

    def load(self, index_dir: Path) -> None:
        self._get_collection(index_dir)

    def search(
            self, query: str, index_dir: Path | None = None, k: int = 10
    ) -> list[tuple[str, float]]:
        if index_dir is not None:
            collection = self._get_collection(index_dir)
        elif self._collection is not None:
            collection = self._collection
        else:
            raise RuntimeError(
                "Vector operators index is not loaded and no index directory provided."
            )

        results = collection.query(
            query_texts=[query],
            n_results=k,
            include=["distances"],
        )

        if not results or not results["ids"] or not results["ids"][0]:
            return []

        result: list[tuple[str, float]] = []
        ids = results["ids"][0]
        distances = results["distances"][0] if results.get("distances") else []

        for doc_id, dist in zip(ids, distances):
            score = 1.0 - float(dist)
            if score > 0.0:
                result.append((doc_id, score))

        return result
