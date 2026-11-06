# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import chromadb
from tqdm import tqdm
from typing import Any
from pathlib import Path
from chromadb.utils import embedding_functions

from src.lib import DocSrc, Tc
from src.utils import PathFinder
from src.utils.decorators import log_execution_time
from src.operators import OpType, OpErrType, operator_error_handler


class VectorOperator:
    """ChromaDB-based semantic indexing and retrieval operator.

    Attributes:
        path_finder: Path helper for vector index storage.
        docsrc_store: In-memory document source map keyed by document id.
        collection_name: ChromaDB collection name.
        embedding_model: Embedding model identifier.
        embedding_func: Embedding function used by the collection.
        _client: Persistent ChromaDB client instance.
        _collection: Active ChromaDB collection instance.
    """

    _BATCH_SIZE = 512

    def __init__(
            self,
            path_finder: PathFinder,
            docsrc_store: dict[str, DocSrc],
            collection_name: str = "ragtm_chunks",
            embedding_model: str = "BAAI/bge-small-en-v1.5",
    ) -> None:
        """Initialize the vector operator configuration.

        Args:
            path_finder: Path helper exposing vector index locations.
            docsrc_store: Document source map used during indexing.
            collection_name: ChromaDB collection name.
            embedding_model: Sentence-transformer model for embeddings.

        """
        self.path_finder: PathFinder = path_finder
        self.docsrc_store: dict[str, DocSrc] = docsrc_store
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model
        )
        self._client: Any | None = None
        self._collection: chromadb.Collection | None = None

    @operator_error_handler(OpType.VCTR, OpErrType.IND)
    def _get_collection(self) -> chromadb.Collection:
        """Load or initialize ChromaDB persistent client and collection."""

        if self._collection is None or self._client is None:
            self.path_finder.vector_dir.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(path=str(self.path_finder.vector_dir))
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_func,  # type: ignore[arg-type]
                metadata={"hnsw:space": "cosine"},
            )

        assert self._collection is not None
        return self._collection

    @operator_error_handler(OpType.VCTR, OpErrType.IND)
    @log_execution_time
    def index(self, target_docs: dict[str, DocSrc] | None = None) -> None:
        """Index or upsert semantic embeddings in ChromaDB.

        Args:
            target_docs: Optional subset of document sources to index.
                When omitted, indexes all documents in the store.

        """

        if target_docs is not None and len(target_docs) == 0:
            return

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
        with tqdm(total=total_chunks,
                  desc=f"{Tc.ylw}[{self.embedding_model}]{Tc.clr} Semantic Indexing",
                  unit="chunk",
                  colour="yellow") as pbar:
            for i in range(0, total_chunks, self._BATCH_SIZE):
                batch_ids = ids[i: i + self._BATCH_SIZE]
                batch_documents = texts[i: i + self._BATCH_SIZE]
                batch_metadatas = metadatas[i: i + self._BATCH_SIZE]

                collection.upsert(
                    ids=batch_ids,
                    documents=batch_documents,
                    metadatas=batch_metadatas,  # type: ignore[arg-type]
                )
                pbar.update(len(batch_ids))

    def load(self) -> None:
        """Ensure the underlying ChromaDB collection is initialized.

        """
        self._get_collection()

    @operator_error_handler(OpType.VCTR, OpErrType.IND)
    def search(
            self, query: str, k: int = 10
    ) -> list[tuple[str, float]]:
        """Run semantic search and convert distances to similarity scores.

        Args:
            query: Query string to search.
            k: Maximum number of results to return.

        Returns:
            List of ``(document_id, score)`` similarity pairs.
        """
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
        distances = []
        raw_distances = results.get("distances")
        if raw_distances is not None and len(raw_distances) > 0:
            distances = raw_distances[0]

        for doc_id, dist in zip(ids, distances):
            score = 1.0 - float(dist)
            if score > 0.0:
                result.append((doc_id, score))

        return result

    @operator_error_handler(OpType.VCTR, OpErrType.IND)
    def delete(self, file_paths: Path | list[Path] | list[str] | set[Path]) -> None:
        """Delete embeddings associated with one or more file paths.

        Args:
            file_paths: Single path or collection of paths to remove.

        """
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
            where={"file_path": {"$in": paths_to_remove}}  # type: ignore[dict-item]
        )
