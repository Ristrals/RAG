# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import chromadb
from typing import Any
from pathlib import Path
from chromadb.utils import embedding_functions

from src.lib import DocSrc, Tc
from src.utils import PathFinder
from src.utils.decorators import log_execution_time


class VectorOperator:
    _BATCH_SIZE = 5000

    def __init__(
            self,
            path_finder: PathFinder,
            docsrc_store: dict[str, DocSrc],
            collection_name: str = "ragtm_chunks",
            embedding_model: str = "BAAI/bge-small-en-v1.5",
    ) -> None:
        self.path_finder: PathFinder = path_finder
        self.docsrc_store: dict[str, DocSrc] = docsrc_store
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model
        )
        self._client: Any | None = None
        self._collection: chromadb.Collection | None = None

    def _get_collection(self) -> chromadb.Collection:
        """Load or initialize ChromaDB persistent client and collection."""

        if self._collection is None or self._client is None:
            self.path_finder.vector_dir.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(path=str(self.path_finder.vector_dir))
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_func,
                metadata={"hnsw:space": "cosine"},
            )

        assert self._collection is not None
        return self._collection

    @log_execution_time
    def index(self, target_docs: dict[str, DocSrc] | None = None) -> None:
        if target_docs is not None and len(target_docs) == 0:
            return

        print(f"{Tc.ylw}[{self. embedding_model}]{Tc.clr} Semantic indexing . . .")
        docs_to_index = self.docsrc_store if target_docs is None else target_docs
        if not docs_to_index:
            return

        collection: chromadb.Collection = self._get_collection()

        ids = list(docs_to_index.keys())
        texts = [
            f"File: {doc.file_path}\nHierarchy: {doc.hierarchy}\n\n{doc.text}"
            for doc in docs_to_index.values()
        ]
        metadatas = [
            {
                "project": doc.project,
                "file_path": str(doc.file_path),
                "hierarchy": doc.hierarchy,
                "content_hash": doc.content_hash,
                "first_character_index": doc.first_character_index,
                "last_character_index": doc.last_character_index,
            }
            for doc in docs_to_index.values()
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

    def load(self) -> None:
        self._get_collection()

    def search(
            self, query: str, k: int = 10
    ) -> list[tuple[str, float]]:
        if self.path_finder.vector_dir is not None:
            collection = self._get_collection()
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

    def delete(self, file_paths: Path | list[Path] | set[Path]) -> None:
        """Removes all vector embeddings associated with file_path(s) from ChromaDB."""
        if self._collection is None:
            self.load()
        if isinstance(file_paths, Path):
            paths_to_remove = [str(file_paths)]
        else:
            paths_to_remove = [str(p) for p in file_paths]
        if not paths_to_remove:
            return
        assert isinstance(self._collection, chromadb.Collection)

        self._collection.delete(
            where={"file_path": {"$in": paths_to_remove}}
        )
